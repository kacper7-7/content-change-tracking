from django.test import TestCase
from django.contrib.auth import get_user_model
from content.models import Content
from notification.models import Notification


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="pwd"
        )
        self.content = Content.objects.create(
            title="Title", body="Body", author=self.user
        )

        self.notification = Notification.objects.create(
            recipient=self.user, content=self.content, message="Test message"
        )

    def test_delete_user_on_cascade(self):
        self.assertEqual(Notification.objects.count(), 1)
        self.content.delete()
        self.assertEqual(Notification.objects.count(), 0)
