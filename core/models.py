from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class Business(models.Model):
    # Choices for business types
    BUSINESS_TYPE_CHOICES = [
        ('grocery', 'Grocery'),
        ('rmg', 'RMG'),
        ('machinery', 'Machinery'),
    ]

    # Fields for your model
    name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    contact = models.CharField(max_length=11)
    email = models.EmailField(null=True)
    bin_no = models.CharField(max_length=20, null=True, blank=True)
    sheet_id = models.CharField(max_length=255, null=True)

    address = models.CharField(verbose_name='Address', max_length=100, null=True, blank=True)
    town = models.CharField(verbose_name='Town/City', max_length=100, null=True, blank=True)
    county = models.CharField(verbose_name='County/Province/State', max_length=100, null=True, blank=True)
    post_code = models.CharField(verbose_name='Post Code', max_length=8, null=True, blank=True)
    country = models.CharField(verbose_name='Country', max_length=40, null=True, blank=True)
    longitude = models.CharField(verbose_name='Longitude', max_length=50, null=True, blank=True)
    latitude = models.CharField(verbose_name='Latitude', max_length=50, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    business_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    captcha_score = models.FloatField(default=0.0)
    has_profile = models.BooleanField(default=False)

    # Foreign key to the user model
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_products')
    cover = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return self.name


class ProductShop(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop = models.ForeignKey(Business, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateField(blank=True, null=True)
    retail_price = models.DecimalField(max_digits=6, decimal_places=2)
    platform_price = models.DecimalField(max_digits=6, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name + '-' + self.shop.name
    

class Order(models.Model):
    from_shop = models.ForeignKey(Business, related_name='from_shop', on_delete=models.CASCADE)
    to_shop = models.ForeignKey(Business, related_name='to_shop', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    has_delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.from_shop.name + ' to ' + self.to_shop.name
    
    
class HubConfiguration(models.Model):
    fare_per_km = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)

    address = models.CharField(verbose_name='Address', max_length=100, null=True, blank=True)
    town = models.CharField(verbose_name='Town/City', max_length=100, null=True, blank=True)
    county = models.CharField(verbose_name='County/Province/State', max_length=100, null=True, blank=True)
    post_code = models.CharField(verbose_name='Post Code', max_length=8, null=True, blank=True)
    country = models.CharField(verbose_name='Country', max_length=40, null=True, blank=True)
    longitude = models.CharField(verbose_name='Longitude', max_length=50, null=True, blank=True)
    latitude = models.CharField(verbose_name='Latitude', max_length=50, null=True, blank=True)

    def __str__(self):
        return "Fare and Hub"