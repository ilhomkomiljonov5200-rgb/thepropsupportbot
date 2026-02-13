import asyncio
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from keyboards import theprop_category_kb, theprop_accounts_kb







from config import (
    TOKEN,
    GROUP_ID,
    ADMIN_LINK,
    WITHDRAW_THREAD,
    NO_ACCOUNT_THREAD,
    TECH_THREAD,
    REMINDER_GROUP_ID
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


def normalize_package(text):
    return text.replace("💰", "").strip()


def usd(amount):
    return f"${amount:,}"


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
        "📢 Eslatma!\n\n"
        "❗ Muammo bormi?\n"
        "👉 @thepropsupportbot ga murojaat qiling\n\n"
        "Support 24/7 ishlaydi ✅"
    )

    while True:
        try:
            await bot.send_message(REMINDER_GROUP_ID, text)
        except:
            pass

        await asyncio.sleep(3600)  # 1 soat


# ================= START =================
@dp.message(F.text == "/start")
async def start(msg: Message):
    clear_state(msg.from_user.id)

    db.add_user(
        user_id=msg.from_user.id,
        full_name=msg.from_user.full_name
    )

    await msg.answer(CHOOSE_ALL, reply_markup=lang_kb())


# ================= MAIN HANDLER =================
@dp.message(F.chat.type == "private")
async def handle(msg: Message):

    uid = msg.from_user.id
    text = msg.text
    lang = get_lang(uid)
    t = TEXTS[lang]

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


    if text in [
        t["pricing"],
        t["register"], t["trade"], t["admin"],
        t["lang"], t["problems"]
    ]:
        clear_state(uid)

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

            header = (
                f"🎫 Ticket #{ticket_id}\n"
                f"👤 {msg.from_user.full_name}\n"
                f"🆔 {uid}"
            )
            await bot.send_message(GROUP_ID, header, message_thread_id=thread)

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
    asyncio.create_task(reminder_loop())  # 🔥 SHU QO‘SHILDI
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
