from core.models import ProductShop


class Cart():
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('session_key')

        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart


    def add(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = {'price': str(product.platform_price)}

        self.session.modified = True

    
    def get_products(self):
        product_ids = self.cart.keys()
        products = ProductShop.objects.filter(id__in=product_ids)

        return products

    
    def __len__(self):
        return len(self.cart)