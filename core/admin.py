from django.contrib import admin
from .models import Business, Category, Brand, Order, Product, ProductShop, FareConfiguration

# Register your models here.
admin.site.register(Business)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(ProductShop)