from django.urls import reverse
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            '/api/v1/register/',
            {'email': 'shopper@example.com', 'username': 'shopper', 'password': 'password'},
        )
        self.assertEqual(response.status_code, 400)

    def test_registration_accepts_valid_password(self):
        response = self.client.post(
            '/api/v1/register/',
            {'email': 'shopper@example.com', 'username': 'shopper', 'password': 'S3cure-shopper!'},
        )
        self.assertEqual(response.status_code, 201)
