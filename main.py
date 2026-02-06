import asyncio
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
        t["lang"], t["problems"], t["back"]
    ]:
        clear_state(uid)

# ================= PRICING MENU =================
    if text == t["pricing"]:
        await msg.answer(
            t["choose_category"],
            reply_markup=theprop_category_kb(lang)
    )
        return


# 🔥🔥🔥 ENG TEPADA BO‘LISHI SHART
# ===== BACK TO MENU =====
    if text == t["back_menu"]:
        await msg.answer(
            t["menu"],
            reply_markup=main_kb(lang)
    )
        return


# ================= CATEGORY CLICK =================
    if text in [t["one_step"], t["two_step"]]:
        await msg.answer(
            t["choose_account"],
            reply_markup=theprop_accounts_kb(lang, t["packages"])
    )
        return


    if text == t["funded"]:
        await msg.answer(
            t["choose_account"],
            reply_markup=theprop_accounts_kb(lang, t["packages"][1:])
    )
        return


# ===== BACK TO CATEGORY =====
    if text == t["back"]:
        await msg.answer(
            t["choose_category"],
            reply_markup=theprop_category_kb(lang)
    )
        return


# ================= PACKAGE CLICK =================
    if text in t["packages"]:
        await msg.answer(
            f"{text} paket tanlandi ✅\n\nAdmin bilan bog‘laning.",
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
        await msg.answer(t["problem_type"], reply_markup=problems_kb(lang))
        return


    # ================= BACK =================
    if text == t["back"]:
        await msg.answer(t["menu"], reply_markup=main_kb(lang))
        return


    # ================= BLOCK IF OPEN =================
    wait_text = {
        "uz": "⏳ Sizning arizangiz ko‘rib chiqilmoqda.\nIltimos sabr qiling.",
        "ru": "⏳ Ваша заявка уже рассматривается.\nПожалуйста подождите.",
        "en": "⏳ Your ticket is being reviewed.\nPlease wait."
    }[lang]

    if has_open_ticket(uid):
        await msg.answer(wait_text)
        return


    # ================= PROBLEM BUTTONS =================
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

# ================= FORWARD =================
    if uid in users_waiting:

        thread = users_waiting.pop(uid)
    ticket_id = db.create_ticket(uid, thread)

    header = (
        f"🎫 Ticket #{ticket_id}\n"
        f"👤 {msg.from_user.full_name}\n"
        f"🆔 {uid}"
    )

    await bot.send_message(GROUP_ID, header, message_thread_id=thread)

    # ===== MEDIA bo‘lsa (rasm/video/file) =====
    if msg.photo or msg.video or msg.document or msg.audio or msg.voice or msg.sticker:

        await bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
            message_thread_id=thread
        )

        # caption bo‘lsa alohida yuboramiz
        if msg.caption:
            await bot.send_message(
                GROUP_ID,
                msg.caption,
                message_thread_id=thread
            )

    # ===== oddiy text bo‘lsa =====
    elif msg.text:
        await bot.send_message(
            GROUP_ID,
            msg.text,
            message_thread_id=thread
        )

    content = msg.text or msg.caption or "[media]"
    db.add_message(ticket_id, "user", content)

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



# ================= ADMIN REPLY =================
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
