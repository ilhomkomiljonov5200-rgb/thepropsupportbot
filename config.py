import os


def _load_local_env():
    for env_name in (".env", "stiker.env", "sticker.env"):
        if not os.path.exists(env_name):
            continue

        with open(env_name, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and (key not in os.environ or not os.environ.get(key, "").strip()):
                    os.environ[key] = value
        break


_load_local_env()


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as err:
        raise ValueError(f"{name} must be an integer, got: {raw}") from err


# ================= BOT =================
TOKEN = (
    os.getenv("BOT_TOKEN", "").strip()
    or os.getenv("TOKEN", "").strip()
    or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
)
if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN yoki TOKEN topilmadi "
        "(Railway ishlatsangiz Variables bo'limida BOT_TOKEN kiriting)"
    )


# ================= GROUP =================
GROUP_ID = _env_int("GROUP_ID", -1003277084936)
REMINDER_GROUP_ID = _env_int("REMINDER_GROUP_ID", -1003485515239)


# ================= TOPICS =================
WITHDRAW_THREAD = _env_int("WITHDRAW_THREAD", 443)
NO_ACCOUNT_THREAD = _env_int("NO_ACCOUNT_THREAD", 2)
TECH_THREAD = _env_int("TECH_THREAD", 444)


# ================= ADMIN =================
ADMIN_LINK = os.getenv("ADMIN_LINK", "https://t.me/thepropsupportuzb").strip()


# ================= AI =================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
