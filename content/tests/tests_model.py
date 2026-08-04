import datetime
from unittest.mock import patch
from django.db import IntegrityError
from django.test import TestCase
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

import content
from content.models import Content, Follow, ContentEditHistory


class FollowModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user5556@example.com",
            password="password"
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

    def test_user_cannot_follow_same_content_twice(self):
        url = reverse("content:follow-list")

        response = self.client.post(url, data={"content": self.content})

        response_follows = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_follows.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_follows.data["results"]), 1)

        with self.assertRaises(IntegrityError):
            Follow.objects.create(
                user=self.user,
                content=self.content
            )

    def test_cascade_delete(self):

        self.assertEqual(Follow.objects.count(), 1)

        self.content.delete()

        self.assertEqual(Follow.objects.count(), 0)

    def test_str_method(self):
        follow = Follow.objects.filter(content=self.content.pk).first()
        self.assertEqual(str(follow), f"{self.user} follows {self.content}")

    @freeze_time("2026-01-01 12:00:00")
    def test_last_viewed_at_is_timezone_now(self):

        content_2 = Content.objects.create(
            author=self.user,
            title="Title-Test",
            body="Body-Test"
        )

        follow_2 = Follow.objects.create(
            user=self.user,
            content=content_2
        )
        expected_time = datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

        self.assertEqual(follow_2.last_viewed_at, expected_time)

class ContentModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user5556@example.com",
            password="password"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.content = Content.objects.create(
            title="Title-Content",
            body="Body-Content",
            author=self.user,
        )

    def test_str_method(self):
        self.assertEqual(str(self.content), self.content.title)

    def test_edit_count_equal_zero(self):
        self.assertEqual(self.content.edited_count, 0)

    def test_delete_user_on_cascade(self):
        self.assertEqual(Content.objects.count(), 1)

        self.user.delete()

        self.assertEqual(Content.objects.count(), 0)


class ContentEditHistoryTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user5556@example.com",
            password="password"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.content = Content.objects.create(
            title="Title-Content",
            body="Body-Content",
            author=self.user,
        )

        self.content_edit_history = ContentEditHistory.objects.create(
            content=self.content
        )

    def test_delete_content_edit_history_on_cascade(self):
        self.assertEqual(ContentEditHistory.objects.count(), 1)

        self.content_edit_history.delete()

        self.assertEqual(ContentEditHistory.objects.count(), 0)
