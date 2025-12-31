"""
Test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_noarmalized(self):
        """ Test email is normalized or new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_river(self):
        """Test creating a river is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        river = models.River.objects.create(
            user=user,
            name='Bear Creek',
            feature='Stream',
            state='AK',
            region=19,
            miles=24.85,
            geometry_type='LineString',
            coordinates=[
                [
                    -159.55596127142,
                    63.8967914977418
                ],
                [
                    -159.55629960491,
                    63.8952464976259
                ],
                [
                    -159.557151821688,
                    63.8904670545064
                ],
                [
                    -159.557229598028,
                    63.8886909430781
                ],
                [
                    -159.557166819625,
                    63.8883009431258
                ],
                [
                    -159.556745707866,
                    63.887534832399
                ],
                [
                    -159.55531792994,
                    63.885438721782
                ],
            ]
        )

        self.assertEqual(str(river), river.name)
