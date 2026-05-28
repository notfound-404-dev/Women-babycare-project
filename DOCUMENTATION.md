# Women and Baby Care Smart Shopping System

## Purpose and Scope
This project is a Django-based e-commerce platform focused on women and baby care products. It provides a complete shopping journey for end users and a management interface for administrators.

## Core Features
### Customer Experience
- Product catalog with category, price, and age-group filters
- Product detail pages with related items
- Cart and checkout flow
- Order history and order tracking views
- Notifications for user activity

### Admin Experience
- Admin panel for managing products, categories, orders, and users
- Dashboard views for operational insights

## Tech Stack
- Django 5.x
- SQLite (default) or MySQL
- HTML/CSS/JavaScript with Bootstrap

## Project Structure (Apps)
- accounts: authentication and user profile
- products: categories, products, and catalog views
- cart: cart and cart items
- orders: checkout, payments, tracking
- personalization: recommendations and search history
- notifications_app: user notifications
- dashboard: admin-facing dashboard views

## Architecture Overview
- Server-rendered Django templates for UI pages
- Static assets served from static/
- Media uploads served from media/ in development
- Modular Django apps for each business area

## Key User Flows
### Browse and Purchase
1) User opens the product list and filters by category, price, or age group.
2) User opens a product detail page and adds item to cart.
3) User proceeds to checkout and places an order.
4) User tracks order status and views order history.

### Admin Management
1) Admin logs in to /admin/.
2) Admin manages categories and products, including images and stock.
3) Admin reviews orders and tracking updates.

## Environment Configuration
Environment variables are defined in .env.example.

- DJANGO_SECRET_KEY: Django secret key
- DJANGO_DEBUG: True or False
- DJANGO_ALLOWED_HOSTS: comma-separated list
- DB_ENGINE: sqlite (default) or mysql
- MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT
- RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET (test mode keys)

## Local Setup
1) Create and activate a virtual environment.
2) Install dependencies:
   pip install -r requirements.txt
3) Configure environment variables using .env.example.
4) Run migrations:
   python manage.py makemigrations
   python manage.py migrate
5) Create an admin user:
   python manage.py createsuperuser
6) Start the server:
   python manage.py runserver

## Database
- Default DB is SQLite at db.sqlite3.
- For MySQL, set DB_ENGINE=mysql and update MYSQL_* values.

## Seed Data
A sample product fixture is available:
- apps/products/fixtures/seed_products.json

Load it with:
  python manage.py loaddata apps/products/fixtures/seed_products.json

## Media and Images
- Media files are stored under media/.
- Product images are stored in media/products/.
- MEDIA_URL is /media/ and is served in DEBUG mode.

## Key Routes
- / : home page
- /products/ : product list
- /products/<id>/ : product detail
- /cart/ : cart pages
- /orders/ : orders and checkout
- /notifications/ : user notifications
- /recommendations/ : personalization views
- /dashboard/ : admin dashboard
- /admin/ : Django admin

## Configuration Notes
- Use a strong DJANGO_SECRET_KEY in production.
- Set DJANGO_DEBUG=False in production.
- Ensure ALLOWED_HOSTS is configured correctly.

## Deployment Notes
- Run database migrations on the server.
- Serve static files using collectstatic and a web server or CDN.
- Serve media files using your web server or an object storage service.

## Maintenance and Updates
- Add new products using the admin panel or fixtures.
- Keep dependencies updated via requirements.txt.
- Monitor and clean unused media files if products are removed.

## Troubleshooting
- Images not showing: ensure product.image is set and DEBUG=True during local development.
- Pagination not showing: only appears when products exceed the paginate_by limit in ProductListView.
