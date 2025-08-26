# ScanAppetite - Canteen & Vendor Ordering System

ScanAppetite is a modern, web-based meal ordering and pickup confirmation system built with Django. It provides a platform for multiple vendors to list their meals and for customers to place orders with per-item pickup scheduling. The system features a robust workflow including invoicing, payment simulation, and a unique barcode-based pickup confirmation process.

## Core Features

### Customer Features
- **Browse Vendors & Meals:** View a homepage with meals grouped by vendor or see a detailed page for a specific vendor.
- **Shopping Cart:** Add multiple meals to a cart.
- **Granular Scheduling:** Select a unique pickup date and time for each individual item in the cart during checkout.
- **Order Placement:** A streamlined checkout process that generates a draft order and an invoice.
- **Order History:** View past and current orders and track the real-time fulfillment status of each item.
- **Barcode Pickup:** Access a unique QR code for each "Ready for Pickup" item and use a camera-based scanner to confirm delivery.

### Vendor Features
- **Vendor Dashboard:** A central, tabbed hub to manage all business activities.
- **Meal Management (CRUD):** Add, edit, and delete meal listings, including name, description, price, and image.
- **Order Fulfillment:** View active order items and update their status through a defined workflow (Confirmed → Processing → Ready for Pickup → Delivered).
- **Barcode Generation:** Generate and print unique barcodes for each order item that is ready for pickup.
- **Bulk Printing:** Select multiple "Ready for Pickup" items and print all their barcodes on a single page.
- ** Rporting:** Vendors can view and print pdf reports date wise.

### Admin Features
- **Full Site Management:** Use the built-in Django Admin site to manage all users, orders, meals, and invoices.

## Tech Stack

* **Backend:** Django, Django REST Framework (for potential API)
* **Frontend:** Django Templates, HTML5, Bootstrap 5, node, ,css, scss, HTMX (for dynamic UI updates)
* **Database:** SQLite (for development), PostgreSQL (recommended for production)
* **Image Handling:** `Pillow`, `sorl-thumbnail` (for creating thumbnails)
* **Barcode/QR Code:** `python-barcode`, `qrcode`
* **Environment Variables:** `python-decouple`
* **Forms:** `django-crispy-forms` with `crispy-bootstrap5`

## Prerequisites

-   Python 3.8+
-   node
-   `pip` (Python package installer)
-   Git

## Setup and Installation Guide

Follow these steps to get the project running on your local machine.

**1. Clone the Repository**
```
git clone https://github.com/FazleRabbbiferdaus172/ScanAppetite.git
cd ScanAppetite
```

**2. Create and Activate Virtual Environment**

On macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```
On Windows:
```
python -m venv venv
venv\Scripts\activate
```
**3. Install Dependencies**
```
pip install -r requirements.txt
```
**4. Set Up Environment Variables**
Create a .env file in the project root directory. Copy the contents of .env.example (if provided) or create it with the following content:
```
SECRET_KEY='your-super-secret-key-here'
DEBUG=True
```
You can generate a new secret key using an online Django secret key generator.

**5. Run Database Migrations**
This will create the database schema based on the models defined in the project.
```
python manage.py migrate
```

**6. Create a Superuser**
This account will have access to the Django Admin site.
```
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

**7. Run the Development Server**
```
python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000/`

## Usage Workflow
1. Admin: Log into the admin site at `/admin/` with your superuser account. You can manage users and change their user_type.

2. Vendor: Register a new user via the "Register as a Vendor" page. Log in, and you will be redirected to your Vendor Dashboard at `/dashboard/`. From there, you can add meals.

3. Customer: Register a new user via the "Register as a Customer" page. Log in, and you will see the homepage. You can add meals to your cart, proceed to the cart to schedule pickup times, and complete the checkout process.

4. Report: Generate and download pdf reports