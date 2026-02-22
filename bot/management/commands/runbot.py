from django.core.management.base import BaseCommand
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
import sys
from dotenv import load_dotenv
import time
import socks
import socket
from django.contrib.auth.models import User
from bot.models import TelegramUser, UserState
from wallet.models import Wallet, Transaction
from shop.models import Product, Order
from django.db import transaction

# تنظیم پروکسی
SOCKS_PORT = 10808
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", SOCKS_PORT)
socket.socket = socks.socksocket

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import imghdr

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telepot.Bot(BOT_TOKEN)

def get_or_create_user(telegram_id, first_name, last_name, username):
    """ایجاد یا دریافت کاربر تلگرام"""
    telegram_user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'username': username
        }
    )
    
    if created:
        django_user = User.objects.create_user(
            username=f"tg_{telegram_id}",
            first_name=first_name or "",
            last_name=last_name or ""
        )
        telegram_user.user = django_user
        telegram_user.save()
        UserState.objects.create(user=telegram_user, current_state='main_menu')
    
    return telegram_user

def main_menu_keyboard():
    """کیبورد منوی اصلی"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 مشاهده محصول", callback_data='view_product')],
        [InlineKeyboardButton(text="💰 کیف پول من", callback_data='wallet_menu')],
        [InlineKeyboardButton(text="📦 سفارش‌های من", callback_data='orders')],
        [InlineKeyboardButton(text="📞 پشتیبانی", callback_data='support')]
    ])
    return keyboard

def wallet_keyboard():
    """کیبورد منوی کیف پول"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 شارژ کیف پول", callback_data='charge_wallet')],
        [InlineKeyboardButton(text="📊 تاریخچه تراکنش‌ها", callback_data='transactions')],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data='back_to_main')]
    ])
    return keyboard

def handle(msg):
    """پردازش پیام‌ها"""
    content_type, chat_type, chat_id = telepot.glance(msg)
    
    if content_type == 'text':
        text = msg['text']
        first_name = msg['from'].get('first_name', '')
        last_name = msg['from'].get('last_name', '')
        username = msg['from'].get('username', '')
        
        telegram_user = get_or_create_user(chat_id, first_name, last_name, username)
        
        if text == '/start':
            welcome_text = (
                f"سلام {first_name}! 👋\n\n"
                "به ربات فروشگاهی خوش اومدی.\n"
                "از منوی زیر انتخاب کن:"
            )
            bot.sendMessage(chat_id, welcome_text, reply_markup=main_menu_keyboard())
            logger.info(f"کاربر جدید: {first_name} - {chat_id}")

def on_callback_query(msg):
    """پردازش دکمه‌های شیشه‌ای"""
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=from_id)
        
        if query_data == 'back_to_main':
            bot.sendMessage(from_id, "منوی اصلی:", reply_markup=main_menu_keyboard())
        
        elif query_data == 'wallet_menu':
            show_wallet(from_id, telegram_user)
        
        elif query_data == 'charge_wallet':
            show_charge_options(from_id)
        
        elif query_data.startswith('charge_'):
            amount = int(query_data.replace('charge_', ''))
            create_charge_request(from_id, telegram_user, amount)
        
        elif query_data == 'transactions':
            show_transactions(from_id, telegram_user)
        
        elif query_data == 'view_product':
            show_product(from_id)
        
        elif query_data == 'buy_product':
            buy_product(from_id, telegram_user)
        
        elif query_data == 'confirm_purchase':
            confirm_purchase(from_id, telegram_user)
            
    except Exception as e:
        logger.error(f"خطا: {e}")
        bot.sendMessage(from_id, "❌ خطایی رخ داد.")

def show_wallet(chat_id, telegram_user):
    """نمایش کیف پول"""
    wallet = Wallet.objects.get(user=telegram_user.user)
    text = f"💰 **کیف پول شما**\n\nموجودی: {wallet.balance:,} تومان"
    bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())

def show_charge_options(chat_id):
    """نمایش گزینه‌های شارژ"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="۵۰,۰۰۰ تومان", callback_data='charge_50000')],
        [InlineKeyboardButton(text="۱۰۰,۰۰۰ تومان", callback_data='charge_100000')],
        [InlineKeyboardButton(text="۲۰۰,۰۰۰ تومان", callback_data='charge_200000')],
        [InlineKeyboardButton(text="۵۰۰,۰۰۰ تومان", callback_data='charge_500000')],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data='wallet_menu')]
    ])
    bot.sendMessage(chat_id, "مبلغ شارژ را انتخاب کن:", reply_markup=keyboard)

def create_charge_request(chat_id, telegram_user, amount):
    """ایجاد درخواست شارژ"""
    with transaction.atomic():
        wallet = Wallet.objects.get(user=telegram_user.user)
        trans = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='deposit',
            status='pending',
            description=f"درخواست شارژ {amount:,} تومان"
        )
    
    # اینجا بعداً درگاه پرداخت وصل میشه
    text = (
        f"✅ درخواست شارژ {amount:,} تومان ثبت شد.\n\n"
        "🔜 به زودی درگاه پرداخت فعال خواهد شد."
    )
    bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())

def show_transactions(chat_id, telegram_user):
    """نمایش تاریخچه تراکنش‌ها"""
    wallet = Wallet.objects.get(user=telegram_user.user)
    transactions = Transaction.objects.filter(wallet=wallet)[:10]
    
    if not transactions:
        bot.sendMessage(chat_id, "📭 تراکنشی یافت نشد.")
        return
    
    text = "📊 **آخرین تراکنش‌ها:**\n\n"
    for t in transactions:
        status_emoji = "✅" if t.status == 'completed' else "⏳"
        text += f"{status_emoji} {t.get_transaction_type_display()}: {t.amount:,} تومان - {t.created_at.strftime('%Y/%m/%d')}\n"
    
    bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())

def show_product(chat_id):
    """نمایش محصول"""
    product = Product.objects.filter(is_active=True).first()
    if not product:
        bot.sendMessage(chat_id, "❌ محصولی موجود نیست.")
        return
    
    text = (
        f"🛍 **{product.name}**\n\n"
        f"{product.description}\n\n"
        f"💰 قیمت: {product.price:,} تومان\n"
        f"📦 موجودی: {product.stock}\n\n"
        "برای خرید از دکمه زیر استفاده کن:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ خرید محصول", callback_data='buy_product')],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data='back_to_main')]
    ])
    bot.sendMessage(chat_id, text, reply_markup=keyboard)

def buy_product(chat_id, telegram_user):
    """خرید محصول"""
    product = Product.objects.filter(is_active=True).first()
    if not product:
        bot.sendMessage(chat_id, "❌ محصولی موجود نیست.")
        return
    
    wallet = Wallet.objects.get(user=telegram_user.user)
    
    if wallet.balance < product.price:
        text = (
            f"❌ موجودی کیف پول شما کافی نیست.\n\n"
            f"موجودی: {wallet.balance:,} تومان\n"
            f"قیمت محصول: {product.price:,} تومان\n\n"
            "لطفاً ابتدا کیف پول خود را شارژ کن."
        )
        bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())
        return
    
    if product.stock < 1:
        bot.sendMessage(chat_id, "❌ محصول موجود نیست.")
        return
    
    text = (
        f"✅ آیا از خرید این محصول مطمئنی؟\n\n"
        f"🛍 {product.name}\n"
        f"💰 قیمت: {product.price:,} تومان\n\n"
        f"موجودی کیف پول شما: {wallet.balance:,} تومان"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تایید خرید", callback_data='confirm_purchase')],
        [InlineKeyboardButton(text="❌ انصراف", callback_data='back_to_main')]
    ])
    bot.sendMessage(chat_id, text, reply_markup=keyboard)

def confirm_purchase(chat_id, telegram_user):
    """تایید نهایی خرید"""
    with transaction.atomic():
        product = Product.objects.filter(is_active=True).first()
        if not product:
            bot.sendMessage(chat_id, "❌ محصولی موجود نیست.")
            return
        
        wallet = Wallet.objects.get(user=telegram_user.user)
        
        if wallet.balance < product.price:
            bot.sendMessage(chat_id, "❌ موجودی کافی نیست.")
            return
        
        if product.stock < 1:
            bot.sendMessage(chat_id, "❌ محصول موجود نیست.")
            return
        
        # کم کردن از کیف پول
        wallet.withdraw(product.price)
        
        # ثبت تراکنش
        trans = Transaction.objects.create(
            wallet=wallet,
            amount=product.price,
            transaction_type='purchase',
            status='completed',
            description=f"خرید {product.name}"
        )
        
        # ثبت سفارش
        order = Order.objects.create(
            user=telegram_user.user,
            product=product,
            quantity=1,
            total_price=product.price,
            status='paid',
            transaction=trans
        )
        
        # کم کردن موجودی محصول
        product.stock -= 1
        product.save()
    
    text = (
        f"✅ **خرید با موفقیت انجام شد!**\n\n"
        f"🛍 محصول: {product.name}\n"
        f"💰 مبلغ پرداخت شده: {product.price:,} تومان\n"
        f"📦 کد سفارش: {order.id}\n\n"
        "از خریدت متشکریم 🙏"
    )
    bot.sendMessage(chat_id, text, reply_markup=main_menu_keyboard())

class Command(BaseCommand):
    help = 'اجرای ربات تلگرام'

    def handle(self, *args, **options):
        self.stdout.write('در حال اجرای ربات...')
        
        if not BOT_TOKEN:
            self.stdout.write(self.style.ERROR('خطا: توکن پیدا نشد!'))
            return
        
        try:
            bot_info = bot.getMe()
            self.stdout.write(self.style.SUCCESS(f"ربات @{bot_info['username']} با موفقیت وصل شد!"))
            
            MessageLoop(bot, {'chat': handle, 'callback_query': on_callback_query}).run_as_thread()
            self.stdout.write(self.style.SUCCESS('ربات در حال اجراست...'))
            
            while True:
                time.sleep(10)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطا: {e}'))
            logger.error(f"خطا: {e}")