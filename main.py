import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from config import (
    TOKEN,
    GROUP_ID,
    ADMIN_LINK,
    WITHDRAW_THREAD,
    NO_ACCOUNT_THREAD,
    TECH_THREAD
)

from texts import TEXTS, CHOOSE_ALL
from db import Database


bot = Bot(TOKEN)
dp = Dispatcher()
db = Database()


# ================= STATES =================
users_lang = {}
users_waiting = {}  # uid -> thread


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
        t["register"], t["trade"], t["admin"],
        t["lang"], t["problems"], t["back"]
    ]:
        clear_state(uid)


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
        await msg.answer(t["problem_type"], reply_markup=problems_kb(lang))
        return


    # ================= BACK =================
    if text == t["back"]:
        await msg.answer(t["menu"], reply_markup=main_kb(lang))
        return


    # =================================================
    # PROBLEM BUTTONS
    # =================================================
    if text == t["withdraw"]:
        users_waiting[uid] = WITHDRAW_THREAD
        await msg.answer(t["withdraw_msg"], disable_web_page_preview=True)
        return

    if text == t["payment"]:
        users_waiting[uid] = NO_ACCOUNT_THREAD
        await msg.answer(t["payment_msg"], disable_web_page_preview=True)
        return

    if text == t["tech"]:
        users_waiting[uid] = TECH_THREAD
        await msg.answer(t["tech_msg"], disable_web_page_preview=True)
        return


    # =================================================
    # FORWARD TO GROUP  ✅ MULTI-LANGUAGE FIX HERE
    # =================================================
    if uid in users_waiting:

        thread = users_waiting.pop(uid)

        ticket_id = db.create_ticket(uid, thread)

        await bot.send_message(
            GROUP_ID,
            f"🎫 Ticket #{ticket_id}\n👤 {msg.from_user.full_name}\n🆔 {uid}\n\n{text}",
            message_thread_id=thread
        )

        db.add_message(ticket_id, "user", text)

        # ✅ NEW: language-based confirm text
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


# =================================================
# ADMIN REPLY SYSTEM
# =================================================
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/reply"))
async def admin_reply(msg: Message):

    try:
        parts = msg.text.split(maxsplit=2)
        ticket_id = int(parts[1])
        answer = parts[2]
    except:
        await msg.reply("❌ Format: /reply 1 text")
        return

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
        f"{reply_prefix} (Ticket #{ticket_id})\n\n{admin_label}:\n{answer}"
    )

    db.add_admin_reply(ticket_id, answer)
    db.close_ticket(ticket_id)

    await msg.reply("✅ Yuborildi va ticket yopildi")

# =================================================
# 📂 ADMIN — OCHIQ TICKETS
# =================================================
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/ochiq"))
async def open_tickets(msg: Message):

    rows = db.cur.execute("""
        SELECT id, user_id
        FROM tickets
        WHERE status='open'
        ORDER BY id DESC
    """).fetchall()

    if not rows:
        await msg.reply("✅ Ochiq ticket yo‘q")
        return

    text = "📂 Ochiq ticketlar:\n\n"

    for r in rows:
        text += f"🎫 #{r['id']} | 👤 {r['user_id']}\n"

    await msg.reply(text)


# =================================================
# 📂 ADMIN — YOPILGAN TICKETS
# =================================================
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/yopilgan"))
async def closed_tickets(msg: Message):

    rows = db.cur.execute("""
        SELECT id, user_id
        FROM tickets
        WHERE status='closed'
        ORDER BY id DESC
    """).fetchall()

    if not rows:
        await msg.reply("❌ Yopilgan ticket yo‘q")
        return

    text = "📁 Yopilgan ticketlar:\n\n"

    for r in rows:
        text += f"🎫 #{r['id']} | 👤 {r['user_id']}\n"

    await msg.reply(text)

# =================================================
# ✅ ADMIN COMMANDS (FIXED FOR @BOTNAME)
# =================================================

# ---------- CLOSE ----------
@dp.message(F.chat.type.in_({"group", "supergroup"}), Command("close"))
async def close_ticket_cmd(msg: Message):

    try:
        ticket_id = int(msg.text.split()[1])
    except:
        await msg.reply("❌ Format: /close 5")
        return

    db.close_ticket(ticket_id)
    await msg.reply(f"🔴 Ticket #{ticket_id} yopildi")


# ---------- OPEN ----------
@dp.message(F.chat.type.in_({"group", "supergroup"}), Command("open"))
async def open_ticket_cmd(msg: Message):

    try:
        ticket_id = int(msg.text.split()[1])
    except:
        await msg.reply("❌ Format: /open 5")
        return

    db.cur.execute(
        "UPDATE tickets SET status='open' WHERE id=?",
        (ticket_id,)
    )
    db.conn.commit()

    await msg.reply(f"🟢 Ticket #{ticket_id} qayta ochildi")


# ---------- STATS ----------
@dp.message(F.chat.type.in_({"group", "supergroup"}), Command("stats"))
async def stats_cmd(msg: Message):

    users = db.cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total = db.cur.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    open_t = db.cur.execute("SELECT COUNT(*) FROM tickets WHERE status='open'").fetchone()[0]
    closed_t = db.cur.execute("SELECT COUNT(*) FROM tickets WHERE status='closed'").fetchone()[0]

    text = (
        "📊 Statistika\n\n"
        f"👤 Users: {users}\n"
        f"🎫 Jami: {total}\n"
        f"🟢 Ochiq: {open_t}\n"
        f"🔴 Yopilgan: {closed_t}"
    )

    await msg.reply(text)




















# ================= RUN =================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
