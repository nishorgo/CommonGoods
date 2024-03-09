from django.shortcuts import render, get_object_or_404
from .cart import Cart
from core.models import ProductShop
from django.http import JsonResponse


def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    return render(request, 'cart/cart_summary.html', {'cart_products': cart_products})


def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product = get_object_or_404(ProductShop, id=product_id)
        cart.add(product=product)
        cart_quantity = cart.__len__()

        response = JsonResponse({'qty': cart_quantity})
        return response


def cart_delete(request):
    pass


def cart_update(request):
    pass