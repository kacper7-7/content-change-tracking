from django.test import TestCase
from django.contrib.auth import get_user_model
from content.models import Content, Follow
from notification.models import Notification
from notification.tasks import create_notification_for_followers_content


class NotificationTaskTest(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            email="author@example.com", password="pwd"
        )
        self.follower_1 = get_user_model().objects.create_user(
            email="f1@example.com", password="pwd"
        )
        self.follower_2 = get_user_model().objects.create_user(
            email="f2@example.com", password="pwd"
        )

        self.content = Content.objects.create(
            title="Title", body="Body", author=self.author
        )

        Follow.objects.create(user=self.follower_1, content=self.content)
        Follow.objects.create(user=self.follower_2, content=self.content)

    def test_task_creates_notifications_for_all_followers(self):

        self.assertEqual(Notification.objects.count(), 0)

        create_notification_for_followers_content(self.content.id)

        self.assertEqual(Notification.objects.count(), 2)

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.follower_1, content=self.content
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.follower_2, content=self.content
            ).exists()
        )

    def test_task_handles_non_existent_content(self):
        create_notification_for_followers_content(99999)

        self.assertEqual(Notification.objects.count(), 0)
