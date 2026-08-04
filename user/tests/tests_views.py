from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class UserViewSetTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password123"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other@example.com", password="password123"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="password123"
        )

        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_create_user_allow_any(self):
        self.client.force_authenticate(user=None)

        url = reverse("user:user-list")

        payload = {
            "email": "new_guest@example.com",
            "password": "securepassword",
            "first_name": "Guest",
        }

        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 4)

    def test_list_users_filters_for_normal_user(self):
        url = reverse("user:user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], self.user.email)

    def test_list_users_for_admin(self):
        url = reverse("user:user-list")
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_update_own_profile(self):
        url = reverse("user:user-detail", kwargs={"pk": self.user.pk})

        response = self.client.patch(url, data={"first_name": "UpdatedName"})
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, "UpdatedName")

    def test_cannot_update_others_profile(self):
        url = reverse("user:user-detail", kwargs={"pk": self.other_user.pk})
        response = self.client.patch(url, data={"first_name": "New-Name"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
