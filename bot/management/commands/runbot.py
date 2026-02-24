# G:\arsalan\programming\telegram-shop-bot\bot\management\commands\runbot.py

from django.core.management.base import BaseCommand
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
import sys
from dotenv import load_dotenv
import time
from django.contrib.auth.models import User
from bot.models import TelegramUser, UserState
from wallet.models import Wallet, Transaction
from shop.models import Product, Order
from django.db import transaction

# تنظیم مسیر
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# بارگذاری متغیرهای محیطی
load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیم هوشمند پروکسی

def setup_smart_proxy():
    """تنظیم پروکسی به صورت هوشمند - هم با پروکسی روشن و هم خاموش کار می‌کنه"""
    
    # پورت‌های رایج v2ray
    proxy_ports = [10808, 10809, 1080, 10800]
    
    for port in proxy_ports:
        try:
            import socks
            import socket
            
            # تست پروکسی
            test_socket = socks.socksocket()
            test_socket.set_proxy(socks.SOCKS5, "127.0.0.1", port)
            test_socket.settimeout(2)
            test_socket.connect(("api.telegram.org", 443))
            test_socket.close()
            
            # اگه وصل شد، پروکسی رو فعال کن
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", port)
            socket.socket = socks.socksocket
            print(f"✅ پروکسی روی پورت {port} فعال شد")
            return True
            
        except:
            continue
    
    print("ℹ️ پروکسی فعالی پیدا نشد - اتصال مستقیم")
    return False

# اجرای تنظیم پروکسی
setup_smart_proxy()

# ساخت نمونه بات
bot = telepot.Bot(BOT_TOKEN)


# توابع کمکی


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

def orders_keyboard():
    """کیبورد منوی سفارشات"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 سفارشات فعال", callback_data='active_orders')],
        [InlineKeyboardButton(text="📜 همه سفارشات", callback_data='all_orders')],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data='back_to_main')]
    ])
    return keyboard

def charge_options_keyboard():
    """کیبورد گزینه‌های شارژ"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="۵۰,۰۰۰ تومان", callback_data='charge_50000')],
        [InlineKeyboardButton(text="۱۰۰,۰۰۰ تومان", callback_data='charge_100000')],
        [InlineKeyboardButton(text="۲۰۰,۰۰۰ تومان", callback_data='charge_200000')],
        [InlineKeyboardButton(text="۵۰۰,۰۰۰ تومان", callback_data='charge_500000')],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data='wallet_menu')]
    ])
    return keyboard

def handle(msg):
    """پردازش پیام‌ها"""
    try:
        if 'text' in msg:
            chat_id = msg['chat']['id']
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
            else:
                bot.sendMessage(chat_id, "❌ لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {e}")

def on_callback_query(msg):
    """پردازش دکمه‌های شیشه‌ای"""
    try:
        query_id = msg['id']
        from_id = msg['from']['id']
        query_data = msg['data']
        
        telegram_user = TelegramUser.objects.get(telegram_id=from_id)
        
        if query_data == 'back_to_main':
            bot.sendMessage(from_id, "منوی اصلی:", reply_markup=main_menu_keyboard())
        
        elif query_data == 'wallet_menu':
            show_wallet(from_id, telegram_user)
        
        elif query_data == 'charge_wallet':
            bot.sendMessage(from_id, "مبلغ شارژ را انتخاب کن:", reply_markup=charge_options_keyboard())
        
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
        
        elif query_data == 'orders':
            bot.sendMessage(from_id, "📦 **مدیریت سفارشات**", reply_markup=orders_keyboard())
        
        elif query_data == 'active_orders':
            show_active_orders(from_id, telegram_user)
        
        elif query_data == 'all_orders':
            show_all_orders(from_id, telegram_user)
        
        elif query_data == 'support':
            bot.sendMessage(from_id, "📞 برای پشتیبانی با ادمین تماس بگیرید: @admin")
            
    except TelegramUser.DoesNotExist:
        bot.sendMessage(from_id, "❌ کاربر یافت نشد. لطفا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در کالبک: {e}")
        try:
            bot.sendMessage(from_id, "❌ خطایی رخ داد.")
        except:
            pass

def show_wallet(chat_id, telegram_user):
    """نمایش کیف پول"""
    try:
        wallet = Wallet.objects.get(user=telegram_user.user)
        text = f"💰 **کیف پول شما**\n\nموجودی: {wallet.balance:,} تومان"
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=telegram_user.user)
        text = f"💰 **کیف پول شما**\n\nموجودی: 0 تومان"
    
    bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())

def create_charge_request(chat_id, telegram_user, amount):
    """ایجاد درخواست شارژ"""
    with transaction.atomic():
        wallet = Wallet.objects.get(user=telegram_user.user)
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='deposit',
            status='pending',
            description=f"درخواست شارژ {amount:,} تومان"
        )
    
    text = f"✅ درخواست شارژ {amount:,} تومان ثبت شد.\n\n🔜 به زودی درگاه پرداخت فعال خواهد شد."
    bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())

def show_transactions(chat_id, telegram_user):
    """نمایش تاریخچه تراکنش‌ها"""
    wallet = Wallet.objects.get(user=telegram_user.user)
    transactions = Transaction.objects.filter(wallet=wallet)[:10]
    
    if not transactions:
        bot.sendMessage(chat_id, "📭 تراکنشی یافت نشد.", reply_markup=wallet_keyboard())
        return
    
    text = "📊 **آخرین تراکنش‌ها:**\n\n"
    for t in transactions:
        status_emoji = "✅" if t.status == 'completed' else "⏳"
        text += f"{status_emoji} {t.get_transaction_type_display()}: {t.amount:,} تومان - {t.created_at.strftime('%Y/%m/%d')}\n"
    
    bot.sendMessage(chat_id, text, reply_markup=wallet_keyboard())

def show_product(chat_id):
    """نمایش محصول با عکس"""
    product = Product.objects.filter(is_active=True).first()
    if not product:
        bot.sendMessage(chat_id, "❌ محصولی موجود نیست.", reply_markup=main_menu_keyboard())
        return
    
    # متن توضیحات محصول
    text = (
        f"🛍 **{product.name}**\n\n"
        f"{product.description}\n\n"
        f"💰 قیمت: {product.price:,} تومان\n"
        f"📦 موجودی: {product.stock}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ خرید محصول", callback_data='buy_product')],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data='back_to_main')]
    ])
    
    # ارسال عکس
    try:
        if product.image:
            # اگه عکس داره، با عکس ارسال کن
            bot.sendPhoto(chat_id, product.image, caption=text, reply_markup=keyboard)
            logger.info(f"عکس محصول {product.name} ارسال شد")
        else:
            # اگه عکس نداره، فقط متن رو بفرست
            text_with_note = text + "\n\n⚠️ برای این محصول عکسی وجود ندارد."
            bot.sendMessage(chat_id, text_with_note, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"خطا در ارسال عکس: {e}")
        # در صورت خطا، فقط متن رو بفرست
        error_text = text + f"\n\n❌ خطا در نمایش عکس"
        bot.sendMessage(chat_id, error_text, reply_markup=keyboard)

def buy_product(chat_id, telegram_user):
    """خرید محصول"""
    product = Product.objects.filter(is_active=True).first()
    if not product:
        bot.sendMessage(chat_id, "❌ محصولی موجود نیست.", reply_markup=main_menu_keyboard())
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
        bot.sendMessage(chat_id, "❌ محصول موجود نیست.", reply_markup=main_menu_keyboard())
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
            bot.sendMessage(chat_id, "❌ محصولی موجود نیست.", reply_markup=main_menu_keyboard())
            return
        
        wallet = Wallet.objects.get(user=telegram_user.user)
        
        if wallet.balance < product.price:
            bot.sendMessage(chat_id, "❌ موجودی کافی نیست.", reply_markup=wallet_keyboard())
            return
        
        if product.stock < 1:
            bot.sendMessage(chat_id, "❌ محصول موجود نیست.", reply_markup=main_menu_keyboard())
            return
        
        wallet.withdraw(product.price)
        
        trans = Transaction.objects.create(
            wallet=wallet,
            amount=product.price,
            transaction_type='purchase',
            status='completed',
            description=f"خرید {product.name}"
        )
        
        order = Order.objects.create(
            user=telegram_user.user,
            product=product,
            quantity=1,
            total_price=product.price,
            status='paid',
            transaction=trans
        )
        
        product.stock -= 1
        product.save()
    
    text = (
        f"✅ **خرید با موفقیت انجام شد!**\n\n"
        f"🛍 محصول: {product.name}\n"
        f"💰 مبلغ: {product.price:,} تومان\n"
        f"📦 کد سفارش: {order.id}\n"
        "از خریدت متشکریم 🙏"
    )
    bot.sendMessage(chat_id, text, reply_markup=main_menu_keyboard())

def show_active_orders(chat_id, telegram_user):
    """نمایش سفارشات فعال"""
    orders = Order.objects.filter(user=telegram_user.user).exclude(status__in=['delivered', 'cancelled'])[:10]
    
    if not orders:
        bot.sendMessage(chat_id, "📭 سفارش فعالی ندارید.", reply_markup=orders_keyboard())
        return
    
    text = "📦 **سفارشات فعال:**\n\n"
    for order in orders:
        status_emoji = {'pending': '⏳', 'paid': '✅', 'processing': '⚙️', 'shipped': '🚚'}.get(order.status, '📦')
        text += f"{status_emoji} سفارش #{order.id} - {order.product.name} - {order.total_price:,} تومان\n"
    
    bot.sendMessage(chat_id, text, reply_markup=orders_keyboard())

def show_all_orders(chat_id, telegram_user):
    """نمایش همه سفارشات"""
    orders = Order.objects.filter(user=telegram_user.user)[:10]
    
    if not orders:
        bot.sendMessage(chat_id, "📭 هیچ سفارشی ندارید.", reply_markup=orders_keyboard())
        return
    
    text = "📜 **همه سفارشات:**\n\n"
    for order in orders:
        status_emoji = {
            'pending': '⏳', 'paid': '✅', 'processing': '⚙️', 
            'shipped': '🚚', 'delivered': '🎉', 'cancelled': '❌'
        }.get(order.status, '📦')
        text += f"{status_emoji} سفارش #{order.id} - {order.product.name} - {order.total_price:,} تومان\n"
    
    bot.sendMessage(chat_id, text, reply_markup=orders_keyboard())

class Command(BaseCommand):
    help = 'اجرای ربات تلگرام'

    def handle(self, *args, **options):
        self.stdout.write('🤖 در حال اجرای ربات...')
        
        if not BOT_TOKEN:
            self.stdout.write(self.style.ERROR('❌ خطا: توکن پیدا نشد!'))
            return
        
        try:
            bot_info = bot.getMe()
            self.stdout.write(self.style.SUCCESS(f"✅ ربات @{bot_info['username']} با موفقیت وصل شد!"))
            
            MessageLoop(bot, {'chat': handle, 'callback_query': on_callback_query}).run_as_thread()
            self.stdout.write(self.style.SUCCESS('🚀 ربات در حال اجراست...'))
            
            while True:
                time.sleep(10)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('🛑 ربات متوقف شد.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطا: {e}'))
            logger.error(f"خطا: {e}")