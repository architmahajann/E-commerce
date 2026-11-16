from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from rest_framework.response import Response
from .serializers import AddToCartSerializer, CartSerializer, CartItemSerializer
from products.models import Product
from rest_framework import status



class CartView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # get or create the cart for logged in user
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
        

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = AddToCartSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        product = input_serializer.validated_data['product']
        quantity = input_serializer.validated_data['quantity']
        
        # get or create the cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # get or create cartitem
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created: # cart item already exist
            # item.quantity = item.quantity + quantity
            if item.quantity + quantity > product.stock:
                return Response({'quantity': 'Requested quantity exceeds available stock.'},
                                status=status.HTTP_400_BAD_REQUEST)
            item.quantity += quantity
            item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ManageCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        # validate
        try:
            change = int(request.data.get('change'))
        except (TypeError, ValueError):
            return Response({"change": "Provide a valid integer change."},
                            status=status.HTTP_400_BAD_REQUEST)
        if change not in (-1, 1):
            return Response({"change": "Change must be -1 or 1."},
                            status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        product = item.product

        # for adding, check the stock
        if change > 0: # change = 1
            if item.quantity + change > product.stock:
                return Response({'error': 'Not enough stock'})
            
        new_qty = item.quantity + change # change can be +1 or -1

        if new_qty <= 0:
            # remove item from cart
            item.delete()
            return Response({'success': 'Item removed'})
        
        # save the new quantity
        item.quantity = new_qty
        item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, item_id):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            
        