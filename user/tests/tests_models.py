from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@example.com", password="password123", first_name="John"
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(str(user), "test@example.com")

    def test_create_user_without_email_raises_error(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")

    def test_create_superuser(self):
        User = get_user_model()
        admin = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

        self.assertEqual(admin.email, "admin@example.com")
        self.assertTrue(admin.check_password("password123"))
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_superuser_with_invalid_flags_raises_error(self):
        User = get_user_model()

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin2@example.com", password="password123", is_staff=False
            )

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin3@example.com", password="password123", is_superuser=False
            )
