from django.core.management.base import BaseCommand
import telepot
from telepot.loop import MessageLoop
import logging
import os
import sys
from dotenv import load_dotenv
import time

# تنظیم پروکسی برای urllib3
import urllib3
urllib3.disable_warnings()

# تنظیم پروکسی برای کل برنامه
import socks
import socket

# پورت v2rayN خودتو اینجا بذار (معمولاً 10808)
SOCKS_PORT = 10808
HTTP_PORT = 10808

# تنظیم پروکسی SOCKS5
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", SOCKS_PORT)
socket.socket = socks.socksocket

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import imghdr

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telepot.Bot(BOT_TOKEN)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    
    if content_type == 'text':
        text = msg['text']
        first_name = msg['from'].get('first_name', 'کاربر')
        
        if text == '/start':
            bot.sendMessage(chat_id, f"سلام {first_name}! به ربات خوش اومدی.")
            logger.info(f"کاربر جدید: {first_name} - {chat_id}")

class Command(BaseCommand):
    help = 'اجرای ربات تلگرام'

    def handle(self, *args, **options):
        self.stdout.write('در حال اجرای ربات...')
        
        if not BOT_TOKEN:
            self.stdout.write(self.style.ERROR('خطا: توکن پیدا نشد!'))
            return
        
        try:
            # تست اتصال
            self.stdout.write('در حال اتصال به تلگرام...')
            bot_info = bot.getMe()
            self.stdout.write(self.style.SUCCESS(f"ربات @{bot_info['username']} با موفقیت وصل شد!"))
            
            MessageLoop(bot, handle).run_as_thread()
            self.stdout.write(self.style.SUCCESS('ربات در حال اجراست...'))
            
            while True:
                time.sleep(10)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطا: {e}'))
            logger.error(f"خطا: {e}")