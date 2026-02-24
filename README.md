# Telegram Shop Bot 🛍️

A powerful single-product Telegram shop bot built with Django and Telepot. This bot allows users to purchase a product using an in-app wallet system.

## 🚀 Features

### Core Features
- **Single Product Shop**: Display and sell one product with image, description, and price
- **Wallet System**: Users can charge their wallet and track balance
- **Order Management**: Complete order history and status tracking
- **Admin Panel**: Full Django admin interface for managing everything
- **Smart Proxy Detection**: Automatically works with/without proxy (V2Ray support)

### Technical Features
- ✅ Django 6.0+ with SQLite database
- ✅ Telepot integration for Telegram Bot API
- ✅ Async message handling
- ✅ Inline keyboards for better UX
- ✅ Transaction management with atomic operations
- ✅ Product image sending with captions
- ✅ User registration and profile management
- ✅ Persian language support (RTL)

## 📋 Prerequisites

- Python 3.10+ (3.14 supported)
- Telegram Bot Token (from @BotFather)
- Git
- (Optional) V2Ray for testing in restricted regions

## 🛠 Installation

### 1. Clone the repository
```bash
git clone https://github.com/reza-khalili-dev/telegram-shop-bot.git
cd telegram-shop-bot



2. Create virtual environment
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate



3. Install dependencies
pip install -r requirements.txt


4. Configure environment variables
TELEGRAM_BOT_TOKEN=your_bot_token_here



5. Run migrations
python manage.py makemigrations
python manage.py migrate



6. Create superuser (for admin panel)
python manage.py createsuperuser



7. Add your product
Run the server: python manage.py runserver

Go to admin panel: http://127.0.0.1:8000/admin

Login with superuser

Add a product with image, description, and price


8. Run the bot
python manage.py runbot



🤖 Bot Commands & Features
User Commands
/start - Welcome message and main menu

Main Menu Options
🛍 View Product - See product details with image

💰 My Wallet - Check balance and charge options

📦 My Orders - View order history

📞 Support - Contact admin

Wallet Options
💳 Charge Wallet - Choose amount (50k, 100k, 200k, 500k Toman)

📊 Transaction History - View last 10 transactions

Order Management
📦 Active Orders - Pending, paid, processing, shipped orders

📜 All Orders - Complete order history with status



🔧 Smart Proxy Configuration
The bot includes intelligent proxy detection for V2Ray users:
# Automatically detects and uses proxy on common ports (10808, 10809, 1080)
# Works with or without proxy - no manual configuration needed