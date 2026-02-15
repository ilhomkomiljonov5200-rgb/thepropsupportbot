import asyncio
import base64
import html
import json
import mimetypes
import random
import re
import urllib.error
import urllib.request
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, MenuButtonWebApp, WebAppInfo, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards import theprop_category_kb, theprop_accounts_kb
from config import (
    TOKEN,
    GROUP_ID,
    ADMIN_LINK,
    WITHDRAW_THREAD,
    NO_ACCOUNT_THREAD,
    TECH_THREAD,
    REMINDER_GROUP_ID,
    OPENAI_API_KEY,
    OPENAI_MODEL
)

from texts import TEXTS, CHOOSE_ALL
from db import Database


bot = Bot(TOKEN)
dp = Dispatcher()
db = Database()


# ================= STATES =================
users_lang = {}
users_waiting = {}  # uid -> thread
users_section = {}  # uid -> active submenu
users_pricing_type = {}  # uid -> one_step | two_step | funded
users_ai_mode = set()
users_ai_images = {}  # uid -> [{"file_id": str, "mime_type": str}]
users_menu_reset = set()  # uid -> menu button reset sent
users_ai_rating_pending = set()
users_ai_connect_wait_msg = {}  # uid -> message_id
users_ai_answer_wait_msg = {}  # uid -> message_id
users_ai_rating_prompt_msg = {}  # uid -> message_id
users_ai_connecting = set()
users_ai_queue_pos = {}  # uid -> queue position

AI_MAX_BUFFER_IMAGES = 30
AI_MAX_IMAGES_PER_REQUEST = 10
AI_END_CHAT_CB = "ai:end_chat"
AI_RATE_CB_PREFIX = "ai:rate:"
MINI_APP_URL = "https://theprop.net"
AI_USER_MEMORY_LIMIT = 6
AI_GLOBAL_MEMORY_LIMIT = 8
AI_MIN_DETAIL_WORDS = 2

DASHBOARD_ISSUE_KEYWORDS = (
    "akkaunt",
    "account",
    "login",
    "log in",
    "dashboard",
    "dashboar",
    "dashbord",
    "dashboarnf",
    "kirmayap",
    "kirolm",
    "qotib",
    "muzlab",
    "ishlamayap",
    "не работает",
    "не могу войти",
    "войти",
    "завис",
    "freez",
    "frozen",
    "stuck",
)

DASHBOARD_DETAIL_KEYWORDS = (
    "parol",
    "password",
    "kod",
    "code",
    "otp",
    "2fa",
    "sms",
    "email",
    "pochta",
    "pocht",
    "xato",
    "error",
    "invalid",
    "captcha",
    "yozsam",
    "kirganda",
    "loginga",
    "парол",
    "код",
    "ошиб",
    "неверн",
    "почт",
    "смс",
)

GENERIC_DASHBOARD_PHRASES = (
    "akkauntga kirmayapti",
    "akkauntga kira olmayapman",
    "accountga kirmayapti",
    "dashboard ishlamayapti",
    "dashboard qotib qolgan",
    "login ishlamayapti",
    "не могу войти",
    "dashboard не работает",
    "can't login",
    "cannot login",
)
LINK_PATTERN = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/|tg://|@[A-Za-z0-9_]{5,})", re.IGNORECASE)


ONE_STEP_OFFERS = {
    "5K": {"balance": 5000, "fee": 49},
    "10K": {"balance": 10000, "fee": 99},
    "25K": {"balance": 25000, "fee": 199},
    "50K": {"balance": 50000, "fee": 299},
    "100K": {"balance": 100000, "fee": 499},
    "200K": {"balance": 200000, "fee": 999},
}


TWO_STEP_OFFERS = {
    "5K": {"balance": 5000, "fee": 35, "daily_pct": 0.04},
    "10K": {"balance": 10000, "fee": 65, "daily_pct": 0.04},
    "25K": {"balance": 25000, "fee": 155, "daily_pct": 0.04},
    "50K": {"balance": 50000, "fee": 265, "daily_pct": 0.04},
    "100K": {"balance": 100000, "fee": 455, "daily_pct": 0.05},
    "200K": {"balance": 200000, "fee": 855, "daily_pct": 0.04},
}


FUNDED_OFFERS = {
    "10K": {"balance": 10000, "fee": 195},
    "25K": {"balance": 25000, "fee": 425},
    "50K": {"balance": 50000, "fee": 825},
    "100K": {"balance": 100000, "fee": 1525},
    "200K": {"balance": 200000, "fee": 2995},
}


# ================= KEYBOARDS =================
def lang_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O‘zbek"),
                   KeyboardButton(text="🇷🇺 Русский"),
                   KeyboardButton(text="🇬🇧 English")]],
        resize_keyboard=True
    )


def main_kb(lang):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["ai_help"])],
            [KeyboardButton(text=t["pricing"])], 
            [KeyboardButton(text=t["register"])],
            [KeyboardButton(text=t["trade"])],
            [KeyboardButton(text=t["problems"])],
            [KeyboardButton(text=t["admin"])],
            [KeyboardButton(text=t["lang"])]
        ],
        resize_keyboard=True
    )


def problems_kb(lang):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["withdraw"])],
            [KeyboardButton(text=t["payment"])],
            [KeyboardButton(text=t["tech"])],
            [KeyboardButton(text=t["back"])]
        ],
        resize_keyboard=True
    )

    

# ================= HELPERS =================
def get_lang(uid):
    return db.get_lang(uid)


def clear_state(uid):
    users_waiting.pop(uid, None)
    users_section.pop(uid, None)
    users_pricing_type.pop(uid, None)
    users_ai_mode.discard(uid)
    users_ai_images.pop(uid, None)
    users_ai_rating_pending.discard(uid)
    users_ai_connect_wait_msg.pop(uid, None)
    users_ai_answer_wait_msg.pop(uid, None)
    users_ai_rating_prompt_msg.pop(uid, None)
    users_ai_connecting.discard(uid)
    users_ai_queue_pos.pop(uid, None)


async def safe_delete_message(chat_id, message_id):
    if not message_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


def message_contains_link(msg: Message):
    for ent in (msg.entities or []):
        if ent.type in {"url", "text_link", "mention"}:
            return True
    for ent in (msg.caption_entities or []):
        if ent.type in {"url", "text_link", "mention"}:
            return True

    # Channel/group forwardlarni ham reklama sifatida ushlaymiz.
    forwarded_chat = getattr(msg, "forward_from_chat", None)
    if forwarded_chat and getattr(forwarded_chat, "type", None) in {"group", "supergroup", "channel"}:
        return True

    text_blob = f"{msg.text or ''}\n{msg.caption or ''}"
    return bool(LINK_PATTERN.search(text_blob))


async def is_admin_in_chat(chat_id: int, user_id: int):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in {"administrator", "creator"}
    except Exception:
        return False


async def replace_queue_message(chat_id, uid, text):
    old_message_id = users_ai_connect_wait_msg.get(uid)
    if old_message_id:
        await safe_delete_message(chat_id, old_message_id)

    sent = await bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
    users_ai_connect_wait_msg[uid] = sent.message_id


def normalize_package(text):
    return text.replace("💰", "").strip()


def usd(amount):
    return f"${amount:,}"


def _short_memory_text(value, limit=180):
    text = re.sub(r"\s+", " ", (value or "").strip())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def build_ai_memory_context(user_id: int):
    user_rows = db.get_ai_user_memory(user_id, limit=AI_USER_MEMORY_LIMIT)
    global_rows = db.get_ai_global_memory(limit=AI_GLOBAL_MEMORY_LIMIT)

    parts = []

    if user_rows:
        rows = list(reversed(user_rows))
        lines = []
        for row in rows:
            q = _short_memory_text(row["user_text"], 130)
            a = _short_memory_text(row["assistant_text"], 130)
            lines.append(f"- User: {q} | Support: {a}")
        parts.append("Memory from this user's previous chats:\n" + "\n".join(lines))

    if global_rows:
        rows = list(reversed(global_rows))
        lines = []
        for row in rows:
            q = _short_memory_text(row["user_text"], 100)
            a = _short_memory_text(row["assistant_text"], 100)
            lines.append(f"- Q: {q} | A: {a}")
        parts.append(
            "General support experience from previous chats (use only as hint, verify with current user details):\n"
            + "\n".join(lines)
        )

    return "\n\n".join(parts).strip()


def looks_like_vague_dashboard_issue(user_text: str):
    text = (user_text or "").strip().lower()
    if not text:
        return False

    has_issue_keyword = any(keyword in text for keyword in DASHBOARD_ISSUE_KEYWORDS)
    if not has_issue_keyword:
        return False

    # Agar foydalanuvchi muammo tafsilotlarini bergan bo'lsa, AI oddiy javob berishi kerak.
    has_detail = any(keyword in text for keyword in DASHBOARD_DETAIL_KEYWORDS)
    if has_detail:
        return False

    words = [w for w in re.split(r"\s+", text) if w]
    if any(phrase in text for phrase in GENERIC_DASHBOARD_PHRASES) and len(words) <= 2:
        return True

    if len(words) <= AI_MIN_DETAIL_WORDS:
        return True

    # Juda qisqa umumiy gap bo'lsa, aniqlik so'raymiz.
    if len(text) < 18:
        return True

    return False


def ai_system_prompt(lang):
    prompts = {
        "uz": (
            "Siz TheProp Live Chat operatorisiz. Savollarning asosiy konteksti theprop.net "
            "platformasi (dashboard, challenge/account bosqichlari, to'lov, payout, qoidalar, login). "
            "Javobni shu kontekstda, qisqa va aniq bering. Keraksiz umumiy IT maslahatlardan qoching, "
            "imkon qadar TheProp bo'yicha amaliy qadamlarga o'ting. Agar aniq bo'lmasa, kerakli "
            "screenshot yoki xato matnini so'rang. Javobni inson support operatoridek yozing. "
            "Bitta javobda faqat 1 ta emoji ishlating. Markdown belgilarini (** ## __) ishlatmang. "
            "Javobda vergul nuqta undov ishlatmang. "
            "Agar foydalanuvchi login/dashboard ishlamayapti deb juda qisqa yozsa, avval muammoni aniqroq so'rang. "
            "Agar memory context berilsa, undan faqat yordamchi kontekst sifatida foydalaning. "
            "Foydalanuvchiga AI ekaningizni aytmang. "
            "Javob tili: o'zbek."
        ),
        "ru": (
            "Вы оператор Live Chat TheProp. Большинство вопросов относится к платформе theprop.net "
            "(dashboard, этапы challenge/account, оплата, payout, правила, вход). Отвечайте именно в "
            "этом контексте, кратко и по делу. Избегайте слишком общих IT-советов, давайте практичные "
            "шаги по TheProp. Если данных мало, попросите нужный скриншот или текст ошибки. "
            "Пишите как человек из поддержки. В одном ответе используйте только 1 эмодзи. "
            "В ответе не используйте запятую точку и восклицательный знак. "
            "Если пользователь слишком коротко пишет, что login/dashboard не работает, сначала попросите подробности. "
            "Если дан memory context, используйте его только как подсказку. "
            "Не используйте Markdown-символы (** ## __). Не говорите пользователю, что вы AI. "
            "Язык ответа: русский."
        ),
        "en": (
            "You are a Live Chat support operator for TheProp. Most questions are about theprop.net "
            "(dashboard, challenge/account stages, payment, payout, rules, login). Answer in that "
            "context, briefly and practically. Avoid generic IT advice when a TheProp-specific action "
            "is possible. If details are missing, ask for the needed screenshot or exact error text. "
            "Write like a human support agent. Use exactly 1 emoji per reply. "
            "Do not use comma period or exclamation mark in replies. "
            "If user says login/dashboard is broken in very short form, first ask for clearer details. "
            "If memory context is provided, use it only as a helpful hint. "
            "Do not use Markdown symbols (** ## __). Never mention being AI. "
            "Response language: English."
        ),
    }
    return prompts.get(lang, prompts["en"])


def prettify_ai_answer(answer: str):
    text = (answer or "").strip()
    if not text:
        return text

    text = text.replace("**", "").replace("__", "")
    # Telegram markdown heading artifacts
    text = text.replace("##", "")
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not raw_lines:
        return text

    plain_text = "\n".join(raw_lines)
    plain_text = re.sub(
        r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u200d\ufe0f]",
        "",
        plain_text,
    )
    plain_text = plain_text.replace(",", "").replace(".", "").replace("!", "")
    plain_text = re.sub(r"[ \t]{2,}", " ", plain_text).strip()
    if not plain_text:
        return "🙂"
    return f"{plain_text} 🙂"


def ai_end_chat_kb(lang):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["ai_end_chat_btn"], callback_data=AI_END_CHAT_CB)]
        ]
    )


def ai_rating_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1. ⭐", callback_data=f"{AI_RATE_CB_PREFIX}1"),
                InlineKeyboardButton(text="2. ⭐", callback_data=f"{AI_RATE_CB_PREFIX}2"),
                InlineKeyboardButton(text="3. ⭐", callback_data=f"{AI_RATE_CB_PREFIX}3"),
                InlineKeyboardButton(text="4. ⭐", callback_data=f"{AI_RATE_CB_PREFIX}4"),
                InlineKeyboardButton(text="5. ⭐", callback_data=f"{AI_RATE_CB_PREFIX}5"),
            ]
        ]
    )




def _push_ai_image(uid, image_ref):
    if not image_ref:
        return

    refs = users_ai_images.setdefault(uid, [])
    refs.append(image_ref)
    if len(refs) > AI_MAX_BUFFER_IMAGES:
        users_ai_images[uid] = refs[-AI_MAX_BUFFER_IMAGES:]


def _chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


async def _build_ai_image_parts(image_refs):
    parts = []

    for ref in image_refs:
        try:
            file = await bot.get_file(ref["file_id"])
            stream = await bot.download_file(file.file_path, timeout=30)
            if not stream:
                continue

            raw = stream.read()
            if not raw:
                continue

            mime_type = ref.get("mime_type") or mimetypes.guess_type(file.file_path)[0] or "image/jpeg"
            if not mime_type.startswith("image/"):
                mime_type = "image/jpeg"

            b64 = base64.b64encode(raw).decode("ascii")
            parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64}",
                    "detail": "low",
                },
            })
        except Exception:
            continue

    if image_refs and not parts:
        raise RuntimeError("Rasmlar yuklab bo'lmadi")

    return parts


async def _ask_ai_once(user_text, lang, image_parts=None, max_tokens=220, memory_context=""):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY topilmadi")

    tried = []
    last_error = None
    models = [OPENAI_MODEL, "gpt-4o-mini"]

    for model in models:
        if model in tried:
            continue
        tried.append(model)
        try:
            return await asyncio.to_thread(
                _call_openai_sync_with_model,
                user_text,
                lang,
                model,
                image_parts or [],
                max_tokens,
                memory_context,
            )
        except RuntimeError as err:
            last_error = err
            reason = str(err)
            # 4xx odatda model bilan ham hal bo'lmaydi, bekor retry qilmaymiz.
            if reason.startswith("HTTP 4") and not reason.startswith("HTTP 408"):
                raise RuntimeError(reason)
            continue

    raise RuntimeError(str(last_error) if last_error else "AI javob topilmadi")


async def ask_ai(user_text, lang, image_parts=None, memory_context=""):
    image_parts = image_parts or []
    user_text = (user_text or "").strip()

    if len(image_parts) <= AI_MAX_IMAGES_PER_REQUEST:
        return await _ask_ai_once(
            user_text,
            lang,
            image_parts=image_parts,
            max_tokens=220,
            memory_context=memory_context,
        )

    chunks = list(_chunked(image_parts, AI_MAX_IMAGES_PER_REQUEST))
    partials = []

    for idx, chunk in enumerate(chunks, start=1):
        chunk_prompt = (
            f"User request: {user_text}\n\n"
            f"You are seeing image batch {idx}/{len(chunks)}."
            " Analyze only this batch and write short findings relevant to the request."
        )
        summary = await _ask_ai_once(
            chunk_prompt,
            lang,
            image_parts=chunk,
            max_tokens=180,
            memory_context=memory_context,
        )
        partials.append(f"Batch {idx}: {summary}")

    final_prompt = (
        f"User request: {user_text}\n\n"
        "Below are findings from multiple image batches.\n"
        "Combine them into one clear final answer:\n\n"
        + "\n\n".join(partials)
    )
    return await _ask_ai_once(
        final_prompt,
        lang,
        image_parts=[],
        max_tokens=260,
        memory_context=memory_context,
    )


def _call_openai_sync_with_model(user_text, lang, model, image_parts, max_tokens, memory_context):
    user_text = (user_text or "").strip()
    if not user_text:
        user_text = "Analyze these images briefly and explain key points."

    if image_parts:
        user_content = [{"type": "text", "text": user_text}, *image_parts]
    else:
        user_content = user_text

    messages = [{"role": "system", "content": ai_system_prompt(lang)}]
    if memory_context:
        messages.append({"role": "system", "content": memory_context})
    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as http_err:
        body = http_err.read().decode("utf-8", errors="replace")
        reason = f"HTTP {http_err.code}"
        try:
            parsed = json.loads(body)
            message = parsed.get("error", {}).get("message")
            if message:
                reason = f"{reason}: {message}"
        except Exception:
            pass
        raise RuntimeError(reason)
    except urllib.error.URLError as url_err:
        raise RuntimeError(f"Network xatosi: {url_err.reason}")
    except TimeoutError:
        raise RuntimeError("Timeout")

    choices = raw.get("choices") or []
    if not choices:
        raise RuntimeError("choices bo'sh")

    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()

    raise RuntimeError("content bo'sh")


def format_one_step_offer(lang, package_key):
    offer = ONE_STEP_OFFERS.get(package_key)
    if not offer:
        return None

    t = TEXTS[lang]
    balance = offer["balance"]
    fee = offer["fee"]
    phase_amount = int(balance * 0.10)
    drawdown_amount = int(balance * 0.06)
    daily_drawdown_amount = int(balance * 0.03)

    return (
        f"📦 {package_key} {t['challenge_label']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💳 {t['fee_label']}: ${fee}\n\n"
        f"📋 {t['rules_title']}:\n"
        f"• 📈 {t['phase_label']}: 10% ({usd(phase_amount)})\n"
        f"• 📉 {t['drawdown_label']}: 6% ({usd(drawdown_amount)})\n"
        f"• 📉 {t['daily_drawdown_label']}: 3% ({usd(daily_drawdown_amount)})\n"
        f"• 📅 {t['min_trade_days_label']}: {t['min_trade_days_value']}\n"
        f"• 💸 {t['first_payout_label']}: {t['first_payout_value']}\n"
        f"• 🤝 {t['profit_split_label']}: 80%\n\n"
        f"✅ {t['news_trading_label']}\n"
        f"✅ {t['weekend_holding_label']}\n\n"
        f"🛒 {t['purchase_label']}: https://theprop.net"
    )


def format_two_step_offer(lang, package_key):
    offer = TWO_STEP_OFFERS.get(package_key)
    if not offer:
        return None

    t = TEXTS[lang]
    balance = offer["balance"]
    fee = offer["fee"]
    phase1_amount = int(balance * 0.08)
    phase2_amount = int(balance * 0.05)
    drawdown_amount = int(balance * 0.10)
    daily_pct = offer["daily_pct"]
    daily_drawdown_amount = int(balance * daily_pct)
    daily_drawdown_pct = int(daily_pct * 100)

    return (
        f"📦 {package_key} {t['challenge_label']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💳 {t['fee_label']}: ${fee}\n\n"
        f"📋 {t['rules_title']}:\n"
        f"• 📈 {t['phase_label']}: 8% ({usd(phase1_amount)})\n"
        f"• 📈 {t['phase2_label']}: 5% ({usd(phase2_amount)})\n"
        f"• 📉 {t['drawdown_label']}: 10% ({usd(drawdown_amount)})\n"
        f"• 📉 {t['daily_drawdown_label']}: {daily_drawdown_pct}% ({usd(daily_drawdown_amount)})\n"
        f"• 📅 {t['min_trade_days_label']}: {t['min_trade_days_value']}\n"
        f"• 💸 {t['first_payout_label']}: {t['first_payout_value']}\n"
        f"• 🤝 {t['profit_split_label']}: 80%\n\n"
        f"✅ {t['news_trading_label']}\n"
        f"✅ {t['weekend_holding_label']}\n\n"
        f"🛒 {t['purchase_label']}: https://theprop.net"
    )


def format_funded_offer(lang, package_key):
    offer = FUNDED_OFFERS.get(package_key)
    if not offer:
        return None

    t = TEXTS[lang]
    balance = offer["balance"]
    fee = offer["fee"]
    drawdown_amount = int(balance * 0.05)
    daily_drawdown_amount = int(balance * 0.03)

    return (
        f"📦 {package_key} {t['funded_offer_label']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💳 {t['fee_label']}: ${fee}\n\n"
        f"📋 {t['rules_title']}:\n"
        f"• 📉 {t['drawdown_label']}: 5% ({usd(drawdown_amount)})\n"
        f"• 📉 {t['daily_drawdown_label']}: 3% ({usd(daily_drawdown_amount)})\n"
        f"• 📅 {t['min_trade_days_label']}: {t['min_trade_days_value']}\n"
        f"• 💸 {t['first_payout_label']}: {t['first_payout_value']}\n"
        f"• 🤝 {t['profit_split_label']}: 80%\n\n"
        f"✅ {t['news_trading_label']}\n"
        f"✅ {t['weekend_holding_label']}\n\n"
        f"🛒 {t['purchase_label']}: https://theprop.net"
    )


# 🔥 OPEN TICKET CHECK
def has_open_ticket(uid):
    row = db.cur.execute(
        "SELECT id FROM tickets WHERE user_id=? AND status='open' LIMIT 1",
        (uid,)
    ).fetchone()
    return row is not None


async def safe_edit(call, text, markup):
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except:
        pass


TICKET_ID_PATTERN = re.compile(r"(?:Ticket|Заявка)\s*#\s*(\d+)", re.IGNORECASE)


def extract_ticket_id_from_reply_chain(msg: Message):
    current = msg.reply_to_message
    depth = 0

    while current and depth < 6:
        for raw in (current.text, current.caption):
            if raw:
                found = TICKET_ID_PATTERN.search(raw)
                if found:
                    return int(found.group(1))
        current = current.reply_to_message
        depth += 1

    return None


def build_ticket_header_and_kb(msg: Message, ticket_id: int):
    uid = msg.from_user.id
    full_name = msg.from_user.full_name or "Unknown user"
    mention_name = html.escape(full_name)
    username = f"@{msg.from_user.username}" if msg.from_user.username else "yo'q"
    profile_url = (
        f"https://t.me/{msg.from_user.username}"
        if msg.from_user.username
        else f"tg://user?id={uid}"
    )

    header = (
        f"🎫 Ticket #{ticket_id}\n"
        f"👤 <a href=\"tg://user?id={uid}\">{mention_name}</a>\n"
        f"🔎 Username: {username}\n"
        f"🆔 ID: {uid}\n"
        f"💬 Tez javob: /reply {ticket_id} text"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Profilni ochish", url=profile_url)]
        ]
    )
    return header, kb


async def send_admin_reply_to_user(msg: Message, ticket_id: int, answer_text: str):
    user_id = db.get_user_by_ticket(ticket_id)
    if not user_id:
        await msg.reply("❌ Ticket topilmadi")
        return

    lang = db.get_lang(user_id)

    reply_prefix = {
        "uz": "📩 Javob",
        "ru": "📩 Ответ",
        "en": "📩 Reply"
    }[lang]

    admin_label = {
        "uz": "👨‍💻 Admin",
        "ru": "👨‍💻 Админ",
        "en": "👨‍💻 Admin"
    }[lang]

    await bot.send_message(
        user_id,
        f"{reply_prefix} (Ticket #{ticket_id})\n\n{admin_label}:\n{answer_text}"
    )

    db.add_admin_reply(ticket_id, answer_text)
    db.close_ticket(ticket_id)

    await msg.reply("✅ Yuborildi va ticket yopildi")





# ================= AUTO REMINDER (NEW) =================
async def reminder_loop():
    text = (
        "📢 Eslatma\n\n"
        "❗ Qanday muammoyingiz bo'lsa\n"
        "💬 @thepropsupportbot ga murojaat qiling\n\n"
        "✅ Support xizmati 24/7 ishlaydi"
    )

    while True:
        try:
            await bot.send_message(REMINDER_GROUP_ID, text)
        except:
            pass

        await asyncio.sleep(7200)  # 2 soat


async def setup_mini_app_button(chat_id=None):
    try:
        await bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(
                text="TheProp",
                web_app=WebAppInfo(url=MINI_APP_URL),
            )
        )
    except Exception as err:
        print(f"⚠️ Mini app tugmasini sozlab bo'lmadi: {err}")


# ================= START =================
@dp.message(F.text == "/start")
async def start(msg: Message):
    clear_state(msg.from_user.id)
    await setup_mini_app_button(msg.chat.id)
    users_menu_reset.add(msg.from_user.id)

    db.add_user(
        user_id=msg.from_user.id,
        full_name=msg.from_user.full_name
    )

    await msg.answer(CHOOSE_ALL, reply_markup=lang_kb())


@dp.message(F.chat.type.in_({"group", "supergroup"}), F.chat.id == REMINDER_GROUP_ID)
async def guard_links_in_reminder_group(msg: Message):
    # Join/leave service xabarlarini tozalaymiz.
    if msg.new_chat_members or msg.left_chat_member:
        try:
            await msg.delete()
        except Exception:
            pass
        return

    if not message_contains_link(msg):
        return

    # Anonymous admin / channel postlarni o'chirmaymiz.
    if not msg.from_user:
        return

    if await is_admin_in_chat(msg.chat.id, msg.from_user.id):
        return

    try:
        await msg.delete()
    except Exception:
        pass


@dp.callback_query(F.data == AI_END_CHAT_CB)
async def ai_end_chat(call: CallbackQuery):
    uid = call.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]

    users_ai_mode.discard(uid)
    users_ai_images.pop(uid, None)
    users_ai_rating_pending.add(uid)

    if call.message:
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        old_rate_prompt_id = users_ai_rating_prompt_msg.pop(uid, None)
        await safe_delete_message(call.message.chat.id, old_rate_prompt_id)
        rating_msg = await bot.send_message(
            call.message.chat.id,
            t["ai_rate_prompt"],
            reply_markup=ai_rating_kb(),
        )
        users_ai_rating_prompt_msg[uid] = rating_msg.message_id

    await call.answer()


@dp.callback_query(F.data.startswith(AI_RATE_CB_PREFIX))
async def ai_rate_chat(call: CallbackQuery):
    uid = call.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]

    if uid not in users_ai_rating_pending:
        await call.answer(t["ai_rate_inactive"], show_alert=True)
        return

    users_ai_rating_pending.discard(uid)
    users_ai_mode.discard(uid)
    users_ai_images.pop(uid, None)

    if call.message:
        rate_prompt_id = users_ai_rating_prompt_msg.pop(uid, None) or call.message.message_id
        await safe_delete_message(call.message.chat.id, rate_prompt_id)
        await bot.send_message(call.message.chat.id, t["ai_rate_thanks"], reply_markup=main_kb(lang))

    await call.answer()


# ================= MAIN HANDLER =================
@dp.message(F.chat.type == "private")
async def handle(msg: Message):

    uid = msg.from_user.id
    text = msg.text
    lang = get_lang(uid)
    t = TEXTS[lang]

    if uid not in users_menu_reset:
        await setup_mini_app_button(msg.chat.id)
        users_menu_reset.add(uid)

    # ================= LANGUAGE =================
    if text in ["🇺🇿 O‘zbek", "🇷🇺 Русский", "🇬🇧 English"]:
        clear_state(uid)

        if "Рус" in text:
            lang = "ru"
        elif "English" in text:
            lang = "en"
        else:
            lang = "uz"

        db.set_lang(uid, lang)
        await msg.answer(TEXTS[lang]["menu"], reply_markup=main_kb(lang))
        return

    if uid in users_ai_connecting and text != t["ai_help"]:
        position = users_ai_queue_pos.get(uid)
        if position:
            await replace_queue_message(
                msg.chat.id,
                uid,
                t["ai_queue_wait"].format(position=position),
            )
        else:
            await replace_queue_message(msg.chat.id, uid, t["ai_wait"])
        return


    if text in [
        t["pricing"],
        t["register"], t["trade"], t["admin"],
        t["lang"], t["problems"], t["ai_help"]
    ]:
        clear_state(uid)

    # ================= AI HELP =================
    if text == t["ai_help"]:
        users_ai_mode.discard(uid)
        users_ai_rating_pending.discard(uid)
        users_ai_connecting.add(uid)

        position = random.randint(5, 15)
        users_ai_queue_pos[uid] = position

        await replace_queue_message(
            msg.chat.id,
            uid,
            t["ai_queue_wait"].format(position=position),
        )

        while uid in users_ai_connecting and position > 1:
            await asyncio.sleep(random.randint(5, 15))
            if uid not in users_ai_connecting:
                return

            position = max(1, position - 1)
            users_ai_queue_pos[uid] = position
            queue_text = t["ai_queue_wait"].format(position=position)
            await replace_queue_message(msg.chat.id, uid, queue_text)

        if uid not in users_ai_connecting:
            return

        users_ai_connecting.discard(uid)
        users_ai_queue_pos.pop(uid, None)
        users_ai_mode.add(uid)
        await safe_delete_message(msg.chat.id, users_ai_connect_wait_msg.pop(uid, None))
        await msg.answer(t["ai_prompt"], reply_markup=ReplyKeyboardRemove())
        return

    # ================= AI MODE =================
    is_image_document = bool(msg.document and (msg.document.mime_type or "").startswith("image/"))
    is_ai_image = bool(msg.photo or is_image_document)
    ai_text = (msg.text or msg.caption or "").strip()

    if uid in users_ai_mode:
        if is_ai_image:
            if msg.photo:
                _push_ai_image(uid, {"file_id": msg.photo[-1].file_id, "mime_type": "image/jpeg"})
            elif is_image_document:
                _push_ai_image(
                    uid,
                    {"file_id": msg.document.file_id, "mime_type": msg.document.mime_type or "image/jpeg"},
                )

            if not ai_text:
                await msg.answer(
                    t["ai_images_buffered"].format(count=len(users_ai_images.get(uid, []))),
                    reply_markup=ReplyKeyboardRemove(),
                )
                return

        if ai_text:
            image_refs = users_ai_images.pop(uid, [])
            try:
                if not image_refs and looks_like_vague_dashboard_issue(ai_text):
                    detail_reply = t["ai_need_details"]
                    db.add_ai_chat_memory(uid, ai_text, detail_reply)
                    await msg.answer(
                        t["ai_reply_pretty"].format(answer=detail_reply),
                        reply_markup=ai_end_chat_kb(lang),
                        disable_web_page_preview=True,
                    )
                    return

                wait_msg = await msg.answer(t["ai_answer_wait"], reply_markup=ReplyKeyboardRemove())
                users_ai_answer_wait_msg[uid] = wait_msg.message_id
                await asyncio.sleep(5)
                image_parts = await _build_ai_image_parts(image_refs) if image_refs else []
                memory_context = build_ai_memory_context(uid)
                answer = await ask_ai(
                    ai_text,
                    lang,
                    image_parts=image_parts,
                    memory_context=memory_context,
                )
                pretty_answer = prettify_ai_answer(answer)
                await safe_delete_message(msg.chat.id, users_ai_answer_wait_msg.pop(uid, None))
                db.add_ai_chat_memory(uid, ai_text, pretty_answer)
                await msg.answer(
                    t["ai_reply_pretty"].format(answer=pretty_answer),
                    reply_markup=ai_end_chat_kb(lang),
                    disable_web_page_preview=True,
                )
            except Exception as err:
                await safe_delete_message(msg.chat.id, users_ai_answer_wait_msg.pop(uid, None))
                reason = str(err).strip()
                if reason:
                    await msg.answer(t["ai_error_reason"].format(reason=reason), reply_markup=ReplyKeyboardRemove())
                else:
                    await msg.answer(t["ai_error"], reply_markup=ReplyKeyboardRemove())
            return

        await msg.answer(t["ai_prompt"], reply_markup=ReplyKeyboardRemove())
        return


# ================= PRICING MENU =================
    if text == t["pricing"]:
        users_section[uid] = "pricing_category"
        await msg.answer(
            t["choose_category"],
            reply_markup=theprop_category_kb(lang)
    )
        return


# 🔥🔥🔥 ENG TEPADA BO‘LISHI SHART
# ===== BACK TO MENU =====
    if text == t["back_menu"]:
        users_section.pop(uid, None)
        await msg.answer(
            t["menu"],
            reply_markup=main_kb(lang)
    )
        return


# ================= CATEGORY CLICK =================
    if text == t["one_step"]:
        users_section[uid] = "pricing_accounts"
        users_pricing_type[uid] = "one_step"
        await msg.answer(
            t["choose_account"],
            reply_markup=theprop_accounts_kb(lang, t["packages"])
    )
        return


    if text == t["two_step"]:
        users_section[uid] = "pricing_accounts"
        users_pricing_type[uid] = "two_step"
        await msg.answer(
            t["choose_account"],
            reply_markup=theprop_accounts_kb(lang, t["packages"])
    )
        return


    if text == t["funded"]:
        users_section[uid] = "pricing_accounts"
        users_pricing_type[uid] = "funded"
        await msg.answer(
            t["choose_account"],
            reply_markup=theprop_accounts_kb(lang, t["packages"][1:])
    )
        return


# ===== BACK ROUTING =====
    if text == t["back"]:
        section = users_section.get(uid)
        if section == "pricing_accounts":
            users_section[uid] = "pricing_category"
            users_pricing_type.pop(uid, None)
            await msg.answer(
                t["choose_category"],
                reply_markup=theprop_category_kb(lang)
        )
            return

        users_section.pop(uid, None)
        users_pricing_type.pop(uid, None)
        await msg.answer(t["menu"], reply_markup=main_kb(lang))
        return


# ================= PACKAGE CLICK =================
    if text in t["packages"]:
        package_key = normalize_package(text)
        pricing_type = users_pricing_type.get(uid)
        users_section.pop(uid, None)
        users_pricing_type.pop(uid, None)

        if pricing_type == "one_step":
            offer_text = format_one_step_offer(lang, package_key)
            if offer_text:
                await msg.answer(offer_text, reply_markup=main_kb(lang))
                return

        if pricing_type == "two_step":
            offer_text = format_two_step_offer(lang, package_key)
            if offer_text:
                await msg.answer(offer_text, reply_markup=main_kb(lang))
                return

        if pricing_type == "funded":
            offer_text = format_funded_offer(lang, package_key)
            if offer_text:
                await msg.answer(offer_text, reply_markup=main_kb(lang))
                return

        await msg.answer(
            t["package_selected"].format(package=package_key),
            reply_markup=main_kb(lang)
        )
        return

    # ================= VIDEOS =================
    if text == t["register"]:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🎥 Video", url="https://t.me/thepropvideo/3")]]
        )
        await msg.answer(t["register"], reply_markup=kb)
        return

    if text == t["trade"]:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🎥 Video", url="https://t.me/thepropvideo/4")]]
        )
        await msg.answer(t["trade"], reply_markup=kb)
        return


    # ================= ADMIN =================
    if text == t["admin"]:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=t["admin"], url=ADMIN_LINK)]]
        )
        await msg.answer(t["admin"], reply_markup=kb)
        return


    # ================= CHANGE LANGUAGE =================
    if text == t["lang"]:
        await msg.answer(t["choose_lang"], reply_markup=lang_kb())
        return


    # ================= PROBLEMS MENU =================
    if text == t["problems"]:
        users_section[uid] = "problems"
        await msg.answer(t["problem_type"], reply_markup=problems_kb(lang))
        return

    # ================= BLOCK IF OPEN =================
    wait_text = {
        "uz": "⏳ Sizning arizangiz ko‘rib chiqilmoqda.\nIltimos sabr qiling.",
        "ru": "⏳ Ваша заявка уже рассматривается.\nПожалуйста подождите.",
        "en": "⏳ Your ticket is being reviewed.\nPlease wait."
    }[lang]

    # ================= PROBLEM BUTTONS =================
    if text == t["withdraw"]:
        if has_open_ticket(uid):
            await msg.answer(wait_text)
            return
        users_waiting[uid] = WITHDRAW_THREAD
        await msg.answer(t["withdraw_msg"], disable_web_page_preview=True)
        return

    if text == t["payment"]:
        if has_open_ticket(uid):
            await msg.answer(wait_text)
            return
        users_waiting[uid] = NO_ACCOUNT_THREAD
        await msg.answer(t["payment_msg"], disable_web_page_preview=True)
        return

    if text == t["tech"]:
        if has_open_ticket(uid):
            await msg.answer(wait_text)
            return
        users_waiting[uid] = TECH_THREAD
        await msg.answer(t["tech_msg"], disable_web_page_preview=True)
        return

    # ================= FORWARD =================
    is_media = bool(msg.photo or msg.video or msg.document or msg.audio or msg.voice or msg.sticker)
    is_content = bool(msg.text or msg.caption or is_media)
    open_ticket_id = db.get_open_ticket(uid)

    if is_content and (uid in users_waiting or open_ticket_id):
        ticket_id = open_ticket_id
        thread = db.get_thread_by_ticket(ticket_id) if ticket_id else None
        created_now = False

        if not ticket_id and uid in users_waiting:
            thread = users_waiting[uid]
            ticket_id = db.create_ticket(uid, thread)
            created_now = True

            header, header_kb = build_ticket_header_and_kb(msg, ticket_id)
            await bot.send_message(
                GROUP_ID,
                header,
                message_thread_id=thread,
                reply_markup=header_kb,
                parse_mode="HTML",
            )

        users_waiting.pop(uid, None)

        if ticket_id and thread:
            if is_media:
                await bot.copy_message(
                    chat_id=GROUP_ID,
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    message_thread_id=thread
                )
            elif msg.text:
                await bot.send_message(
                    GROUP_ID,
                    msg.text,
                    message_thread_id=thread
                )

            content = msg.text or msg.caption or "[media]"
            db.add_message(ticket_id, "user", content)

            if created_now:
                confirm_text = {
                    "uz": f"✅ Ticket #{ticket_id} qabul qilindi\n\n",
                    "ru": f"✅ Заявка #{ticket_id} принята\n\n",
                    "en": f"✅ Ticket #{ticket_id} received\n\n"
                }[lang]

                if thread == WITHDRAW_THREAD:
                    await msg.answer(confirm_text + t["withdraw_done"], reply_markup=main_kb(lang))
                elif thread == NO_ACCOUNT_THREAD:
                    await msg.answer(confirm_text + t["payment_done"], reply_markup=main_kb(lang))
                else:
                    await msg.answer(confirm_text + t["tech_done"], reply_markup=main_kb(lang))

            return

    if has_open_ticket(uid):
        await msg.answer(wait_text)
        return



# ================= ADMIN REPLY =================
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/reply"))
async def admin_reply(msg: Message):
    if msg.chat.id != GROUP_ID:
        return

    try:
        parts = msg.text.split(maxsplit=2)
        ticket_id = int(parts[1])
        answer = parts[2]
    except:
        await msg.reply("❌ Format: /reply 1 text")
        return

    await send_admin_reply_to_user(msg, ticket_id, answer)


@dp.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def admin_reply_by_reply(msg: Message):
    if msg.chat.id != GROUP_ID:
        return

    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        return
    if msg.reply_to_message.from_user.id != bot.id:
        return

    if msg.text and msg.text.startswith("/"):
        return

    answer = msg.text or msg.caption
    if not answer:
        await msg.reply("❌ Javob matni bo‘sh")
        return

    ticket_id = extract_ticket_id_from_reply_chain(msg)
    if not ticket_id:
        await msg.reply("❌ Ticket topilmadi. Ticket xabariga reply qiling")
        return

    await send_admin_reply_to_user(msg, ticket_id, answer)
# ================= ADMIN COMMANDS (NEW) =================

# /stats
@dp.message(F.chat.type.in_({"group", "supergroup"}), Command("stats"))
async def stats_cmd(msg: Message):

    users = db.cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    open_tickets = db.cur.execute("SELECT COUNT(*) FROM tickets WHERE status='open'").fetchone()[0]
    closed = db.cur.execute("SELECT COUNT(*) FROM tickets WHERE status='closed'").fetchone()[0]

    await msg.reply(
        f"📊 Statistika\n\n"
        f"👤 Users: {users}\n"
        f"🟢 Ochiq: {open_tickets}\n"
        f"🔴 Yopilgan: {closed}"
    )


# /ochiq
@dp.message(F.chat.type.in_({"group", "supergroup"}), Command("ochiq"))
async def open_list(msg: Message):

    rows = db.cur.execute(
        "SELECT id, user_id FROM tickets WHERE status='open' ORDER BY id DESC LIMIT 20"
    ).fetchall()

    if not rows:
        return await msg.reply("Ochiq ticket yo‘q")

    text = "🟢 Ochiq ticketlar:\n\n"

    for t in rows:
        text += f"#{t[0]} | {t[1]}\n"

    await msg.reply(text)


# /yopilgan
@dp.message(F.chat.type.in_({"group", "supergroup"}), Command("yopilgan"))
async def closed_list(msg: Message):

    rows = db.cur.execute(
        "SELECT id, user_id FROM tickets WHERE status='closed' ORDER BY id DESC LIMIT 20"
    ).fetchall()

    if not rows:
        return await msg.reply("Yopilgan ticket yo‘q")

    text = "🔴 Yopilgan ticketlar:\n\n"

    for t in rows:
        text += f"#{t[0]} | {t[1]}\n"

    await msg.reply(text)


# /open 5
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/open "))
async def reopen_ticket(msg: Message):
    try:
        ticket_id = int(msg.text.split()[1])
    except:
        return await msg.reply("❌ Format: /open 5")

    db.cur.execute("UPDATE tickets SET status='open' WHERE id=?", (ticket_id,))
    db.conn.commit()

    await msg.reply(f"✅ Ticket #{ticket_id} qayta ochildi")


# /close 5
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/close "))
async def close_ticket_cmd(msg: Message):
    try:
        ticket_id = int(msg.text.split()[1])
    except:
        return await msg.reply("❌ Format: /close 5")

    db.close_ticket(ticket_id)

    await msg.reply(f"🔴 Ticket #{ticket_id} yopildi")


# ================= RUN =================
async def main():
    await setup_mini_app_button()
    asyncio.create_task(reminder_loop())  
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
