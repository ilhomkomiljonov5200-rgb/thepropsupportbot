import os


# ================= BOT =================
# Railway / server environment variable dan olinadi
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN topilmadi! Environment variable qo‘sh: TOKEN= ")


# ================= GROUP =================
GROUP_ID = -1003277084936


# ================= TOPICS (THREADS) =================
WITHDRAW_THREAD = 443      # 💸 Pul yechish
NO_ACCOUNT_THREAD = 2      # ❌ To‘lov qildim akkaunt bermadi
TECH_THREAD = 444          # ⚠️ Hisob/Dashboard ishlamay


# ================= ADMIN =================
ADMIN_LINK = "https://t.me/thepropsupportuzb"
