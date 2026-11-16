from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from products.models import Product


class CartApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='shopper@example.com', username='shopper', password='S3cure-shopper!'
        )
        self.client.force_authenticate(self.user)
        self.product = Product.objects.create(name='Bottle', price='10.00', stock=2)

    def test_add_to_cart_validates_stock(self):
        response = self.client.post(
            '/api/v1/cart/add/', {'product_id': self.product.id, 'quantity': 3}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_to_cart_returns_cart(self):
        response = self.client.post(
            '/api/v1/cart/add/', {'product_id': self.product.id, 'quantity': 1}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['quantity'], 1)
