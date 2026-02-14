import os
from pathlib import Path
from dotenv import load_dotenv

# Optional local env files for development.
# In Railway, variables come from platform env and these files may not exist.
BASE_DIR = Path(__file__).resolve().parent
for env_name in (".env", "stiker.env", "sticker.env"):
    env_path = BASE_DIR / env_name
    if env_path.exists():
        load_dotenv(env_path, override=False)


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
    "",
).strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
