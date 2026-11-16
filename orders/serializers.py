from rest_framework import serializers
from .models import Order, OrderItem


class ShippingAddressSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=15)
    city = serializers.CharField(max_length=20)
    state = serializers.CharField(max_length=20)
    zipCode = serializers.CharField(max_length=10)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ('id', 'user', 'subtotal', 'tax_amount', 'grand_total', 'status', 'created_at')