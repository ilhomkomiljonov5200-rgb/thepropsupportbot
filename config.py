import os


# ================= BOT =================
# 🔥 LOCAL TEST (VS Code)
# Tokenni shu yerga yozamiz
TOKEN = "8361728289:AAGNkF9zdtEao4Rff4w27aE0cV6vqbQ2WdM"


# ================= GROUP =================
GROUP_ID = -1003277084936
REMINDER_GROUP_ID = -1002293269329


# ================= TOPICS =================
WITHDRAW_THREAD = 443
NO_ACCOUNT_THREAD = 2
TECH_THREAD = 444


# ================= ADMIN =================
ADMIN_LINK = "https://t.me/thepropsupportuzb"


# ================= AI =================
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "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",
).strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
