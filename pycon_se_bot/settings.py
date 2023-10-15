import os

from aiogram import Dispatcher
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
REDIS_HOST = os.getenv("REDIS_HOST")
GF_SECURITY_ADMIN_USER = os.getenv("GF_SECURITY_ADMIN_USER")
GF_SECURITY_ADMIN_PASSWORD = os.getenv("GF_SECURITY_ADMIN_PASSWORD")
dp = Dispatcher()
