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
            self.cart[product_id] = {'price': str(product.platform_price), 'quantity': 1}

        self.session.modified = True

    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        self.cart[product_id]['quantity'] = product_qty

        self.session.modified = True


    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
        
        self.session.modified = True


    def total(self):
        total = 0.0
        
        for product_id, product_info in self.cart.items():
            price = float(product_info['price'])
            total += price * product_info['quantity']
        
        return round(total, 2)
    
    
    def get_products(self):
        product_ids = self.cart.keys()
        products = ProductShop.objects.filter(id__in=product_ids).select_related('product', 'shop')

        product_info = {}
        for product in products:
            product_id = str(product.id)
            product_info[product_id] = {
                'id': product.id,
                'product_name': product.product.name,
                'shop_name': product.shop.name,
                'price': product.platform_price,
                'quantity': self.cart[product_id]['quantity'], 
            }

        return product_info

    
    def __len__(self):
        return len(self.cart)