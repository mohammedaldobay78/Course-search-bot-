# config.py
import os
from dotenv import load_dotenv
load_dotenv(".env")

# Telegram / Admin
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Webhook / App
APP_URL = os.getenv("APP_URL", "")  # e.g. https://your-app.onrender.com
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")  # you can change, ensure SECRET
WEBHOOK_URL = APP_URL.rstrip("/") + WEBHOOK_PATH

# SerpAPI
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# TON wallet address (display to users)
TON_WALLET_ADDRESS = os.getenv("TON_WALLET_ADDRESS", "")

# Database (Postgres)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@host:5432/dbname")

# Points/prices (final approved)
POINTS_PER_SEARCH = int(os.getenv("POINTS_PER_SEARCH", "10"))
POINTS_UPLOAD = int(os.getenv("POINTS_UPLOAD", "100"))
POINTS_VIP_MONTH = int(os.getenv("POINTS_VIP_MONTH", "30"))

# Points packages (final approved)
POINTS_PACKAGES = {
    "100": {"points": 100, "price_ton": float(os.getenv("PRICE_100_TON", "0.5"))},
    "250": {"points": 250, "price_ton": float(os.getenv("PRICE_250_TON", "1.0"))},
    "500": {"points": 500, "price_ton": float(os.getenv("PRICE_500_TON", "2.0"))},
}

# Misc
LOG_FILE = os.getenv("LOG_FILE", "bot.log")
TEMP_SESSION_EXPIRY = 3600  # seconds