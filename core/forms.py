from django import forms
from django.core import validators
from .models import Brand, Business, Product, ProductShop

class RegisterBusinessForm(forms.ModelForm):
    name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your business name...'}))
    contact = forms.CharField(max_length=11, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your contact number...'}))
    email = forms.CharField(max_length=11, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your email address...'}))
    bin_no = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your BIN number...'}))
    sheet_id = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Google Sheet ID number...'}))

    token = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Business
        fields = ('name', 'contact', 'email', 'bin_no', 'sheet_id', 'business_type')


class BusinessAddressForm(forms.ModelForm):
    address = forms.CharField(max_length=100, required=True, widget=forms.HiddenInput())
    town = forms.CharField(max_length=100, required=True, widget=forms.HiddenInput())
    county = forms.CharField(max_length=100, required=True, widget=forms.HiddenInput())
    post_code = forms.CharField(max_length=8, required=True, widget=forms.HiddenInput())
    country = forms.CharField(max_length=40, required=True, widget=forms.HiddenInput())
    longitude = forms.CharField(max_length=50, required=True, widget=forms.HiddenInput())
    latitude = forms.CharField(max_length=50, required=True, widget=forms.HiddenInput())

    class Meta:
        model = Business
        fields = ('address', 'town', 'county', 'post_code', 'country', 'longitude', 'latitude')


class OrderForm(forms.Form):
    def __init__(self, *args, product_shop=None, **kwargs):
        super().__init__(*args, **kwargs)

        if product_shop:
            self.fields['quantity'].validators.append(
                validators.MaxValueValidator(
                    product_shop.quantity,
                    message="Quantity cannot exceed available stock."
                ) 
            )

    quantity = forms.IntegerField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Type quantity'})
    )



class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class CreateProductShopForm(forms.ModelForm):
    class Meta:
        model = ProductShop
        exclude = ['shop']

        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }