from collections import defaultdict
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

from .forms import RegisterBusinessForm, BusinessAddressForm, CreateProductForm, CreateProductShopForm, OrderForm, HubConfigureForm
from .models import Business, Category, Product, ProductShop, Order, HubConfiguration
from .maps import calculate_distance, get_directions, reverse_geocode
from .forecast import exp_smoothing_forecast
from .sheets import access_sheets, sort_sheet_data, sync_data_with_sheet
from config.mixins import AjaxFormMixin, reCAPTCHAValidation, FormErrors, RedirectParams, Directions

result = 'ERROR'
message = 'There was an error, please try again.'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def get_user_shops(request):
    return Business.objects.filter(user=request.user)


def homepage_view(request):
    product_name = request.GET.get('product_name', '')
    shop_name = request.GET.get('shop_name', '')

    categories = Category.objects.all()

    if request.user.is_authenticated:
        product_shops = ProductShop.objects.select_related('product__category', 'product__brand', 'shop').exclude(shop__user=request.user)
    else:
        product_shops = ProductShop.objects.select_related('product__category', 'product__brand', 'shop')

    query = ''

    if product_name and shop_name:
        products = product_shops.filter(
            Q(product__name__icontains=product_name) & Q(shop__name__icontains=shop_name)
        ).order_by('product__name')
        query = product_name
    elif product_name:
        products = product_shops.filter(product__name__icontains=product_name)
        query = product_name
    elif shop_name:
        products = product_shops.filter(shop__name__icontains=shop_name)
        query = shop_name
    else:
        products = product_shops.all().order_by('product__name')

    context = {
        'categories': categories,
        'products': products, 
        'query': query,
        'default_image_url': settings.DEFAULT_PRODUCT_IMAGE_URL,
    }

    return render(request, 'core/home.html', context)


class RegisterBusiness(AjaxFormMixin, FormView):
    template_name = 'core/register_business.html'
    form_class = RegisterBusinessForm
    success_url = 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recaptcha_site_key'] = settings.RECAPTCHA_KEY
        return context
    
    def form_valid(self, form):
        response = super(AjaxFormMixin, self).form_valid(form)
        if is_ajax(self.request):
            token = form.cleaned_data.get('token')
            captcha = reCAPTCHAValidation(token)

            if captcha['success']:
                obj = form.save(commit=False)
                obj.user = self.request.user
                obj.captcha_score = float(captcha['score'])
                obj.save()

                result = 'SUCCESS'
                message = 'Thank you for joining us.'

            data = {'result': result, 'message': message}
            return JsonResponse(data)
        
        return response
    

def address_view(request, shop_id):
    user = request.user
    form = BusinessAddressForm(instance=user)
    shop = get_object_or_404(Business, id=shop_id)


    if is_ajax(request):
        form = BusinessAddressForm(data=request.POST, instance=user)
        if form.is_valid():
            shop.address = form.cleaned_data['address']
            shop.town = form.cleaned_data['town']
            shop.county = form.cleaned_data['county']
            shop.post_code = form.cleaned_data['post_code']
            shop.country = form.cleaned_data['country']
            shop.longitude = form.cleaned_data['longitude']
            shop.latitude = form.cleaned_data['latitude']
            shop.has_profile = True
            shop.save()
            
            result = 'SUCCESS'
            message = 'Your address has been updated.'
        else:
            message = FormErrors(form)
        
        data = {'result': result, 'message': message}
        return JsonResponse(data)
    
    else:
        context = {'form': form}
        context['google_api_key'] = settings.GOOGLE_API_KEY
        context['base_country'] = settings.BASE_COUNTRY
        context['shop'] = shop

        return render(request, 'core/address.html', context)
    
        
def hub_configuration_view(request):
    config = None
    try:
        config = HubConfiguration.objects.get()
    except HubConfiguration.DoesNotExist:
        pass  # No action needed if the instance doesn't exist 

    if request.method == 'POST':
        if config:  # Check if config exists
            form = HubConfigureForm(request.POST, instance=config) 
        else:
            form = HubConfigureForm(request.POST) 

        if form.is_valid():
            form.save()
            return JsonResponse({'result': 'SUCCESS', 'message': 'Hub details succesfully updated'})  
        else:
            message = FormErrors(form)
            return JsonResponse({'result': 'Error', 'message': message})  

    # Initial GET request handling:
    form = HubConfigureForm(instance=config)  # Create the form even if config doesn't exist
    context = {
        'form': form, 
        'config': config, 
        'google_api_key': settings.GOOGLE_API_KEY,
        'base_country': settings.BASE_COUNTRY
    }
    return render(request, 'core/hub_configuration.html', context)


def order_view(request):
    cart = request.session.get('session_key', {})
    error = None

    for product_id, product_info in cart.items():
        product = get_object_or_404(ProductShop, id=int(product_id))
        quantity = product_info['quantity']

        if quantity > product.quantity:
            error = "Quantity cannot exceed available stock."
        else:
            hub = HubConfiguration.objects.get()
            hub_coordinate = (hub.latitude, hub.longitude)

            from_shop = product.shop
            from_shop_coordinate = (from_shop.latitude, from_shop.longitude)

            to_shop = request.user.business
            to_shop_coordinate = (to_shop.latitude, to_shop.longitude)

            distance = calculate_distance(from_shop_coordinate, to_shop_coordinate)
            distance += calculate_distance(hub_coordinate, from_shop_coordinate)
            delivery_charge = distance * float(hub.fare_per_km)

            with transaction.atomic():
                order = Order(
                    from_shop=from_shop,
                    to_shop=to_shop,
                    product=product.product,
                    quantity=quantity,
                    distance=distance,
                    delivery_charge=delivery_charge
                )
                order.save()

                product.quantity -= quantity
                product.save()

                if 'session_key' in request.session:
                    del request.session['session_key']
                    request.session.modified = True 

            return redirect('order_success')


def complete_delivery_view(request):
    undelivered_orders = Order.objects.filter(has_delivered=False)

    for order in undelivered_orders:
        order.has_delivered = True
        order.save()

    return redirect('home')


def revenue_view(request):
    completed_orders = Order.objects.filter(has_delivered=True)

    total = 0
    for order in completed_orders:
        total += order.delivery_charge

    return render(request, 'core/revenue.html', {'orders': completed_orders, 'total': total})


def direction_view(request):
    undelivered_orders = Order.objects.filter(has_delivered=False)
    hub = HubConfiguration.objects.get()
    
    locations = [{'lat': float(hub.latitude), 'lng': float(hub.longitude), 'title': 'Central Hub', 'index': 1}]
    seen_locations = set()
    index = 2
    for order in undelivered_orders:
        from_location = (order.from_shop.latitude, order.from_shop.longitude)
        to_location = (order.to_shop.latitude, order.to_shop.longitude)

        if (from_location, to_location) not in seen_locations:
            locations.append({'lat': float(order.from_shop.latitude), 'lng': float(order.from_shop.longitude), 'title': order.from_shop.name, 'index': index})
            locations.append({'lat': float(order.to_shop.latitude), 'lng': float(order.to_shop.longitude), 'title': order.to_shop.name, 'index': index+1})
            index += 2

            seen_locations.add((from_location, to_location))


    directions = get_directions(locations)
    route = directions['routes'][0]

    leg_data = []
    for leg in route['legs']:
        origin_coords = (leg['start_location']['lat'], leg['start_location']['lng'])
        origin_address = reverse_geocode(origin_coords)

        destination_coords = (leg['end_location']['lat'], leg['end_location']['lng'])
        destination_address = reverse_geocode(destination_coords)

        steps = []
        for step in leg['steps']:
            steps.append(step['html_instructions'])

        leg_info = {
            'distance': leg['distance']['text'],
            'duration': leg['duration']['text'],
            'origin_address': origin_address,  
            'destination_address': destination_address,
            'steps': steps
        }

        leg_data.append(leg_info)


    context = {
        'key': settings.GOOGLE_API_KEY,
        'locations': locations[1:-1],
        'origin': locations[0],
        'destination': locations[-1],
        'legs': leg_data
    }

    return render(request, 'core/direction.html', context)


def route(request):
    undelivered_orders = Order.objects.filter(has_delivered=False)
    
    locations = []
    for order in undelivered_orders:
        locations.append({'lat': order.from_shop.latitude, 'lng': order.from_shop.longitude})
        locations.append({'lat': order.to_shop.latitude, 'lng': order.to_shop.longitude})

    context = {
        "locations": locations,
        "google_api_key": settings.GOOGLE_API_KEY,
        "base_country": settings.BASE_COUNTRY
    }
    return render(request, 'core/route.html', context)


def map(request):

	lat_a = request.GET.get("lat_a", None)
	long_a = request.GET.get("long_a", None)
	lat_b = request.GET.get("lat_b", None)
	long_b = request.GET.get("long_b", None)
	lat_c = request.GET.get("lat_c", None)
	long_c = request.GET.get("long_c", None)
	lat_d = request.GET.get("lat_d", None)
	long_d = request.GET.get("long_d", None)


	#only call API if all 4 addresses are added
	if lat_a and lat_b and lat_c and lat_d:
		directions = Directions(
			lat_a= lat_a,
			long_a=long_a,
			lat_b = lat_b,
			long_b=long_b,
			lat_c= lat_c,
			long_c=long_c,
			lat_d = lat_d,
			long_d=long_d
			)
	else:
		return redirect(reverse('route'))

	context = {
        "google_api_key": settings.GOOGLE_API_KEY,
        "base_country": settings.BASE_COUNTRY,
        "lat_a": lat_a,
        "long_a": long_a,
        "lat_b": lat_b,
        "long_b": long_b,
        "lat_c": lat_c,
        "long_c": long_c,
        "lat_d": lat_d,
        "long_d": long_d,
        "origin": f'{lat_a}, {long_a}',
        "destination": f'{lat_b}, {long_b}',
        "directions": directions,
	}

	return render(request, 'core/map.html', context)


def business_list(request):
    # Fetch all shops associated with the user
    user_shops = Business.objects.filter(user=request.user)

    return render(request, 'core/business_list.html', {'shops': user_shops})


def shop_detail(request, shop_id):
    shop = get_object_or_404(Business, id=shop_id)

    # Retrieve the search query from the URL parameters
    query = request.GET.get('q', '')
    products_in_shop = ProductShop.objects.filter(shop=shop).select_related('product', 'product__brand')

    if query:
        # If there is a search query, filter products based on the query
        products = products_in_shop.filter(
            Q(product__name__icontains=query) | Q(product__brand__name__icontains=query)
        ).order_by('product__name')
    else:
        # If there is no search query, show all products for the shop
        products = products_in_shop.all().order_by('product__name')

    return render(request, 'core/shop_detail.html', {'shop': shop, 'products': products, 'query': query})


def create_product(request, shop_id):
    if request.method == 'POST':
        form = CreateProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # Redirect to the ProductShop form with the created product's ID and shop ID as a query parameter
            return redirect(reverse('create_product_shop', kwargs={'shop_id': shop_id, 'product_id': product.id}))
    else:
        form = CreateProductForm()

    return render(request, 'core/create_product.html', {'form': form})


def create_product_shop(request, shop_id, product_id):
    product = get_object_or_404(Product, id=product_id)
    shop = get_object_or_404(Business, id=shop_id)

    if request.method == 'POST':
        form = CreateProductShopForm(request.POST)
        if form.is_valid():
            product_shop = form.save(commit=False)
            product_shop.product = product
            product_shop.shop = shop
            product_shop.save()

            # Redirect to a success page or another view
            return redirect(reverse('business_list'))  # Replace with your desired success page or view
    else:
        form = CreateProductShopForm()

    return render(request, 'core/create_productshop.html', {'form': form, 'product': product})


def authenticate_google_sheets(request):
    if request.method == 'POST':
        access_sheets()

    return render(request, 'core/authenticate_google_sheets.html')


def auth_callback(request):
    return HttpResponse('Authentication successful. You can now access Google Sheets.')


def merge_database(request, shop_id):
    shop = get_object_or_404(Business, id=shop_id)
    sheet = shop.sheet_id
    sync_data_with_sheet(shop_id, sheet)

    return render(request, 'core/merge_database.html', {'shop_id': shop_id})


def expired_date_alert_view(request):
    shops = Business.objects.all()

    for shop in shops:
        recipient_email = shop.email

        today = datetime.now().date()
        five_days_from_today = today + timedelta(days=5)

        product_expriration_within_five_days = ProductShop.objects.filter(
            shop_id=shop.id,
            expiration_date__gte=today,
            expiration_date__lte=five_days_from_today
        )

        context = {
            'products': product_expriration_within_five_days
        }

        if product_expriration_within_five_days:
            html_msg = render_to_string('core/email.html', context=context)
            plain_msg = strip_tags(html_msg)

            message = EmailMultiAlternatives(
                subject='These products are about to expire',
                body=plain_msg,
                from_email=None,
                to=[recipient_email]
            )

            message.attach_alternative(html_msg, 'text/html')
            message.send()     
    
    messages.success(request, "Products to be expired have been mailed. Cheers!")
    return redirect('success_mail')


def success_mail(request):
    success_message = None
    storage = messages.get_messages(request)
    for message in storage:
        success_message = message

    return render(request, 'core/success_mail.html', {'message': success_message})


def forecast_view(request):
    result = exp_smoothing_forecast()

    return render(request, 'core/forecast.html', {'forecasts': result})


def success_order(request):
    return render(request, 'core/order_confirmed.html')