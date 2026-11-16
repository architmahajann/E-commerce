from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from carts.models import Cart, CartItem
from products.models import Product


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class CheckoutApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='shopper@example.com', username='shopper', password='S3cure-shopper!'
        )
        self.client.force_authenticate(self.user)
        self.product = Product.objects.create(name='Bottle', price='10.00', stock=2)
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

    def test_checkout_reduces_stock_and_clears_cart(self):
        response = self.client.post(
            '/api/v1/orders/place/',
            {'shippingAddress': {
                'address': '10 Main Street', 'phone': '5551234567',
                'city': 'Austin', 'state': 'TX', 'zipCode': '78701',
            }},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)
        self.assertFalse(CartItem.objects.filter(cart__user=self.user).exists())

    def test_checkout_validates_shipping_details(self):
        response = self.client.post('/api/v1/orders/place/', {'shippingAddress': {}}, format='json')
        self.assertEqual(response.status_code, 400)
