# Women and Baby Care Smart Shopping System

## Stack
- Django (Python)
- MySQL
- HTML/CSS/JavaScript (Bootstrap)

## Apps
- `accounts` (auth + profile)
- `products` (catalog + filters)
- `cart` (shopping cart)
- `orders` (checkout, payment simulation, tracking)
- `personalization` (recommendations + search history)
- `notifications_app` (user notifications)
- `dashboard` (admin analytics view)

## Documentation
See `DOCUMENTATION.md` for full project documentation.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment values from `.env.example`
3. Run migrations: `python manage.py makemigrations && python manage.py migrate`
4. Create admin user: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`
