from django.db import transaction
from kombu.exceptions import OperationalError as BrokerOperationalError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.models import Cart
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer, ShippingAddressSerializer
from .tasks import send_order_notification_task


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        address_serializer = ShippingAddressSerializer(
            data=request.data.get('shippingAddress')
        )
        address_serializer.is_valid(raise_exception=True)
        shipping_address = address_serializer.validated_data

        with transaction.atomic():
            cart = Cart.objects.select_for_update().filter(user=request.user).first()
            if not cart or not cart.items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            items = list(cart.items.select_related('product').all())
            product_ids = [item.product_id for item in items]
            products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(id__in=product_ids)
            }
            for item in items:
                product = products[item.product_id]
                if product.stock < item.quantity:
                    return Response(
                        {'details': f'Only {product.stock} is left for {product.name}'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            order = Order.objects.create(
                user=request.user,
                subtotal=cart.subtotal,
                tax_amount=cart.tax_amount,
                grand_total=cart.grand_total,
                address=shipping_address['address'],
                phone=shipping_address['phone'],
                city=shipping_address['city'],
                state=shipping_address['state'],
                zip_code=shipping_address['zipCode'],
            )
            for item in items:
                product = products[item.product_id]
                product.stock -= item.quantity
                product.save(update_fields=['stock'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                    total_price=item.total_price,
                )
            cart.items.all().delete()

        try:
            send_order_notification_task.apply_async(
                args=(order.pk,),
                ignore_result=True,
                retry=False,
                expires=300,
            )
        except (BrokerOperationalError, TimeoutError, ConnectionError):
            pass
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class MyOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'orderitem_set__product'
        )


class OrderDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_object(self):
        order = get_object_or_404(Order, pk=self.kwargs['pk'], user=self.request.user)
        return Order.objects.prefetch_related('orderitem_set__product').get(pk=order.pk)
