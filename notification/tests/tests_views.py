from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from content.models import Content
from notification.models import Notification


class NotificationViewSetTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="pwd"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other@example.com", password="pwd"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.content = Content.objects.create(
            title="Title", body="Body", author=self.other_user
        )

        self.my_notification = Notification.objects.create(
            recipient=self.user, content=self.content, message="Your notification"
        )

        self.other_notification = Notification.objects.create(
            recipient=self.other_user,
            content=self.content,
            message="Other user notification",
        )

    def test_list_notifications_returns_only_mine(self):
        url = reverse("notification:notification-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.my_notification.id)
        self.assertEqual(response.data["results"][0]["message"], "Your notification")

    def test_unauthenticated_access_is_blocked(self):
        self.client.force_authenticate(user=None)

        url = reverse("notification:notification-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_notification_manually(self):
        url = reverse("notification:notification-list")

        payload = {"content": self.content.pk, "message": "Hacked notification"}
        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Notification.objects.count(), 2)

    def test_cannot_delete_notification(self):
        url = reverse(
            "notification:notification-detail", kwargs={"pk": self.my_notification.pk}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(
            Notification.objects.filter(id=self.my_notification.id).exists()
        )

    def test_cannot_update_notification(self):
        url = reverse(
            "notification:notification-detail", kwargs={"pk": self.my_notification.pk}
        )

        response = self.client.patch(url, data={"message": "Changed"})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
