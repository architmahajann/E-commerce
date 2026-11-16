from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    tax_percent = serializers.DecimalField(source='product.tax_percent', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('id', 'cart', 'product_name', 'price', 'tax_percent', 'total_price')

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        product = getattr(self.instance, 'product', None)
        if product and value > product.stock:
            raise serializers.ValidationError(f'Only {product.stock} units are available.')
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'items', 'subtotal', 'tax_amount', 'grand_total')


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True), source='product'
    )
    quantity = serializers.IntegerField(min_value=1, max_value=1000)

    def validate(self, attrs):
        if attrs['quantity'] > attrs['product'].stock:
            raise serializers.ValidationError({'quantity': 'Requested quantity exceeds available stock.'})
        return attrs

        