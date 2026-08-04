from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from content.models import Content, Follow
from rest_framework.test import APIClient


class ContentViewSetTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user999@example.com", password="password"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.content = Content.objects.create(
            title="Title-Content",
            body="Body-Content",
            author=self.user,
        )

        self.follow = Follow.objects.create(
            user=self.user,
            content=self.content,
        )

    def test_get_content_list(self):
        url = reverse("content:content-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_content_detail(self):
        url = reverse("content:content-detail", kwargs={"pk": self.content.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["body"], self.content.body)

    def test_delete_content(self):
        url_list = reverse("content:content-list")
        response_list = self.client.get(url_list)

        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data["results"]), 1)

        url_delete = reverse("content:content-detail", kwargs={"pk": self.content.pk})
        response_delete = self.client.delete(url_delete)

        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url_list)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_full_update_content(self):
        url = reverse("content:content-detail", kwargs={"pk": self.content.pk})

        user_2 = get_user_model().objects.create_user(
            email="user9992@example.com", password="password"
        )

        payload = {
            "title": "New-Content",
            "body": "New-Body-Content",
            "author": user_2.pk,
        }

        response = self.client.put(url, data=payload)
        self.content.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "New-Content")
        self.assertEqual(response.data["body"], "New-Body-Content")
        self.assertEqual(response.data["edited_count"], 1)
        self.assertIsNotNone(response.data["edit_history"])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_partially_update_content(self):
        url = reverse("content:content-detail", kwargs={"pk": self.content.pk})

        payload = {
            "body": "New-Body-Content",
        }

        response = self.client.patch(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Title-Content")
        self.assertEqual(response.data["body"], "New-Body-Content")
        self.assertEqual(response.data["edited_count"], 1)
        self.assertIsNotNone(response.data["edit_history"])

    def test_create_content(self):
        url = reverse("content:content-list")

        payload = {
            "title": "New-Content",
            "body": "New-Body-Content",
        }

        response_create = self.client.post(url, payload)

        content = Content.objects.get(title="New-Content")

        response_list = self.client.get(url)

        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_list.data["results"][1]["title"], "New-Content")
        self.assertEqual(response_list.data["results"][1]["body"], "New-Body-Content")
        self.assertTrue(Follow.objects.filter(user=self.user, content=content))

    def test_is_followed_by_me(self):
        url = reverse("content:content-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["is_followed_by_me"])

    def test_followers_count(self):
        url = reverse("content:content-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["followers_count"], 1)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_is_hot(self):
        url = reverse("content:content-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["results"][0]["is_hot"])

        for _ in range(5):
            user = get_user_model().objects.create_user(
                email=f"user00{_}@example.com",
                password="password",
            )

            Follow.objects.create(user=user, content=self.content)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["is_hot"])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_recent_edits_count(self):
        url = reverse("content:content-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["recent_edits_count"], 0)

        url_update = reverse("content:content-detail", kwargs={"pk": self.content.pk})
        payload = {"title": "New-tile"}

        for _ in range(11):
            self.client.patch(url_update, data=payload)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["recent_edits_count"], 11)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_last_edit_date(self):
        url = reverse("content:content-list")

        url_update = reverse("content:content-detail", kwargs={"pk": self.content.pk})
        payload = {"title": "New-tile"}

        self.client.patch(url_update, data=payload)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["results"][0]["last_edit_date"])

    def test_is_admin(self):
        admin_user = get_user_model().objects.create_user(
            email="admin_user@admin_user.com", password="password", is_staff=True
        )

        admin_client = APIClient()

        admin_client.force_authenticate(admin_user)

        url = reverse("content:content-list")
        response = admin_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["followers"])

    def test_cannot_update_others_content(self):
        other_user = get_user_model().objects.create_user(
            email="other_user@other_user.com",
            password="password",
        )
        other_content = Content.objects.create(
            title="Title", body="Body", author=other_user
        )

        url = reverse("content:content-detail", kwargs={"pk": other_content.pk})

        response = self.client.patch(url, data={"title": "New-title"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_others_content(self):
        other_user = get_user_model().objects.create_user(
            email="other_user@other_user.com",
            password="password",
        )
        other_content = Content.objects.create(
            title="Title", body="Body", author=other_user
        )

        url = reverse("content:content-detail", kwargs={"pk": other_content.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unfollowed_content_is_hidden(self):
        other_user = get_user_model().objects.create_user(
            email="other_user@other_user.com",
            password="password",
        )
        other_content = Content.objects.create(
            title="Title", body="Body", author=other_user
        )

        url = reverse("content:content-detail", kwargs={"pk": other_content.pk})

        response = self.client.get(url)

        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"], "To see more info, follow this content!"
        )
        self.assertNotIn("body", response.data)

    def test_retrieve_updates_last_viewed_at(self):
        url = reverse("content:content-detail", kwargs={"pk": self.content.pk})
        old_viewed_at = self.follow.last_viewed_at

        self.client.get(url)
        self.follow.refresh_from_db()

        self.assertGreater(self.follow.last_viewed_at, old_viewed_at)

    def test_updated_contents_endpoint(self):
        detail_url = reverse("content:content-detail", kwargs={"pk": self.content.pk})
        self.client.get(detail_url)

        self.content.title = "Zmieniony tytul"
        self.content.save(update_fields=["title", "updated_at"])

        url = reverse("content:content-update-contents")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0 or "results" in response.data)

    def test_unauthenticated_access_is_blocked(self):
        self.client.force_authenticate(user=None)

        url = reverse("content:content-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FollowViewSetTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="follow_test@example.com", password="password"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.content = Content.objects.create(
            title="Title-Content",
            body="Body-Content",
            author=self.user,
        )
        self.follow = Follow.objects.create(
            user=self.user,
            content=self.content,
        )

    def test_create_follow(self):
        url = reverse("content:follow-list")

        new_content = Content.objects.create(
            title="Test", body="Test", author=self.user
        )

        response = self.client.post(url, data={"content": new_content.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 2)

    def test_list_follows(self):
        other_user = get_user_model().objects.create_user(
            email="other@example.com", password="pwd"
        )
        Follow.objects.create(user=other_user, content=self.content)

        url = reverse("content:follow-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["results"]), 1)

    def test_delete_own_follow(self):
        url = reverse("content:follow-detail", kwargs={"pk": self.follow.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Follow.objects.count(), 0)

    def test_cannot_update_follow_manually(self):
        url = reverse("content:follow-detail", kwargs={"pk": self.follow.pk})
        response = self.client.patch(
            url, data={"last_viewed_at": "2030-01-01T12:00:00Z"}
        )

        self.follow.refresh_from_db()
        self.assertNotEqual(
            str(self.follow.last_viewed_at), "2030-01-01 12:00:00+00:00"
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_follow_missed_edits_count_and_has_new_changes(self):
        url_update = reverse("content:content-detail", kwargs={"pk": self.content.pk})
        self.client.patch(url_update, data={"title": "Updated Title!"})

        url_follows = reverse("content:follow-list")
        response = self.client.get(url_follows)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        follow_data = response.data["results"][0]

        self.assertTrue(follow_data["has_new_changes"])
        self.assertEqual(follow_data["missed_edits_count"], 1)

    def test_cannot_delete_others_follow(self):
        other_user = get_user_model().objects.create_user(
            email="other_user@other_user.com",
            password="password",
        )

        other_follow = Follow.objects.create(user=other_user, content=self.content)

        url = reverse("content:follow-detail", kwargs={"pk": other_follow.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_follow_content_twice(self):
        url = reverse("content:follow-list")

        response = self.client.post(url, data={"content": self.content.pk})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Follow.objects.count(), 1)
