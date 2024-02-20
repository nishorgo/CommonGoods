# Common Goods: A B2B Wholesale Marketplace

This Django-powered platform provides a space for vendors to connect and transact business for wholesale goods. Streamline your B2B transactions and discover new suppliers within our convenient marketplace.

## Key Features

* **Vendor-to-Vendor Transactions:** Buy and sell products directly from other businesses in a streamlined wholesale environment.
* **Google Sheets Integration:** Synchronize your existing inventory and product data with our platform via Google Sheets for ease of use.  
* **Custom Delivery Service:** Benefit from our in-house delivery service using Google Maps API integration for accurate routing and on-time deliveries. 
* **Reasonable Pricing:** Facilitation of cost-effective deals between vendors.

## Technologies

* **Python/Django:** Core web application framework.
* **Google Sheets API:** Enables synchronization of product and inventory data.
* **Google Maps API:** Route generation and location services for delivery management.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nishorgo/CommonGoods.git

2. **Install dependecies:**
   ```bash
   pipenv install

3. **Set up environment variables:**
   Provide keys for relevant APIs
    ```
    GOOGLE_API_KEY
    RECAPTCHA_KEY
    RECAPTCHA_SECRET_KEY
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD
    ```

4. **Run migrations:**
   ```bash
    python manage.py makemigrations
    python manage.py migrate

5. **Start the development server:**
   ```bash
    python manage.py runserver

## Contributions
Contributions are welcome! If you want to contribute to this project, feel free to open a pull request.

## License
**MIT License**

Copyright (c) 2024 Abid Hasan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
