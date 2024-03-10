from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage_view, name='home'),
    path('hub/', views.hub_configuration_view, name='hub'),
    path('register/', views.RegisterBusiness.as_view(), name='register_business'),
    path('business/', views.business_list, name='business_list'),
    path('order/', views.order_view, name='order'),
    path('order_success/', views.success_order, name='order_success'),
    path('revenue/', views.revenue_view, name='revenue'),
    path('complete_delivery/', views.complete_delivery_view, name='complete_delivery'),
    path('business/<int:shop_id>', views.shop_detail, name='shop_detail'),
    path('business/<int:shop_id>/address/', views.address_view, name='shop_address'),
    path('business/<int:shop_id>/merge_database/', views.merge_database, name='merge_database'),
    path('business/<int:shop_id>/product/create/', views.create_product, name='create_product'),
    path('business/<int:shop_id>/productshop/create/<int:product_id>/', views.create_product_shop, name='create_product_shop'),
    path('authenticate_google_sheets/', views.authenticate_google_sheets, name='authenticate_google_sheets'),
    path('auth_callback/', views.auth_callback, name='auth_callback'),
    path('direction/', views.direction_view, name='direction'),
    path('forecast/', views.forecast_view, name='forecast'),
    path('mail_success/', views.success_mail, name='success_mail'),
    path('mail_expired_products/', views.expired_date_alert_view, name='mail_expired_products'),
]
