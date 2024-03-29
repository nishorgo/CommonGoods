from django.shortcuts import render, get_object_or_404
from .cart import Cart
from core.models import ProductShop
from django.http import JsonResponse

import json


def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    total = cart.total()
    return render(request, 'cart/cart_summary.html', {'cart_products': cart_products, 'total': total})


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
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})
        return response
    

def cart_update(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        cart_qty = {}
        data_list = request.POST.getlist('quantities') 
        quantities = json.loads(data_list[0])
        if quantities:
            for product_id, quantity in quantities.items():
                cart.update(product=product_id, quantity=quantity)
                cart_qty[product_id] = quantity

        response = JsonResponse(cart_qty)
        return response