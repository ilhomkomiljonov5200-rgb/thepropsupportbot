from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

from config import (
    GROUP_ID,
    WITHDRAW_THREAD,
    NO_ACCOUNT_THREAD,
    TECH_THREAD,
    ADMIN_LINK
)

# ================= STATES =================
users_lang = {}
users_waiting = {}


# ================= TEXTS (3 TIL) =================
TEXTS = {

    "uz": {
        "menu": "Menu 👇",
        "problems": "🛠 TheProp muammolari",
        "back": "⬅️ Orqaga",

        "withdraw": "💸 Pul yechishda muammo",
        "payment": "❌ To‘lov qildim, akkaunt berilmadi",
        "tech": "⚠️ Hisob/dashbord ishlamayapti",

        "withdraw_msg":
            "📩 Iltimos, muammoingizni batafsil yozib qoldiring.\n\n"
            "🔐 Login va parolingizni yuboring.\n\n"
            f"👉 {ADMIN_LINK}",

        "payment_msg":
            "🎥 https://t.me/thepropvideo/2\n\n"
            "Videodagidek ro‘yxatdan o‘ting.\n\n"
            "🔐 Login va parolni yuboring.\n\n"
            f"👉 {ADMIN_LINK}",

        "tech_msg":
            "📩 Muammoni yozib qoldiring.\n\n"
            f"👉 {ADMIN_LINK}"
    },


    "ru": {
        "menu": "Меню 👇",
        "problems": "🛠 Проблемы TheProp",
        "back": "⬅️ Назад",

        "withdraw": "💸 Проблема с выводом",
        "payment": "❌ Оплатил, аккаунт не дали",
        "tech": "⚠️ Аккаунт/дашборд не работает",

        "withdraw_msg":
            "📩 Опишите проблему подробно.\n\n"
            "🔐 Отправьте логин и пароль.\n\n"
            f"👉 {ADMIN_LINK}",

        "payment_msg":
            "🎥 https://t.me/thepropvideo/2\n\n"
            "Зарегистрируйтесь как показано в видео.\n\n"
            "🔐 Отправьте логин и пароль.\n\n"
            f"👉 {ADMIN_LINK}",

        "tech_msg":
            "📩 Опишите проблему.\n\n"
            f"👉 {ADMIN_LINK}"
    },


    "en": {
        "menu": "Menu 👇",
        "problems": "🛠 TheProp Issues",
        "back": "⬅️ Back",

        "withdraw": "💸 Withdrawal problem",
        "payment": "❌ Paid but no account",
        "tech": "⚠️ Dashboard not working",

        "withdraw_msg":
            "📩 Please describe the issue.\n\n"
            "🔐 Send login & password.\n\n"
            f"👉 {ADMIN_LINK}",

        "payment_msg":
            "🎥 https://t.me/thepropvideo/2\n\n"
            "Register as shown in the video.\n\n"
            "🔐 Send login & password.\n\n"
            f"👉 {ADMIN_LINK}",

        "tech_msg":
            "📩 Describe the issue.\n\n"
            f"👉 {ADMIN_LINK}"
    }
}


# ================= HELPERS =================
def get_lang(uid):
    return users_lang.get(uid, "uz")


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


# ================= REGISTER =================
def register(dp):

    # ---------- language set ----------
    @dp.message(F.text.in_(["🇺🇿 O‘zbek", "🇷🇺 Русский", "🇬🇧 English"]))
    async def set_lang(msg: Message):
        if "O‘zbek" in msg.text:
            users_lang[msg.from_user.id] = "uz"
        elif "Русский" in msg.text:
            users_lang[msg.from_user.id] = "ru"
        else:
            users_lang[msg.from_user.id] = "en"

        lang = get_lang(msg.from_user.id)
        await msg.answer(TEXTS[lang]["menu"])


    # ---------- open problems ----------
    @dp.message(lambda m: m.text in [TEXTS[x]["problems"] for x in TEXTS])
    async def open_problems(msg: Message):
        lang = get_lang(msg.from_user.id)
        await msg.answer("👇", reply_markup=problems_kb(lang))


    # ---------- choose problem ----------
    @dp.message(F.chat.type == "private")
    async def handle(msg: Message):

        uid = msg.from_user.id
        lang = get_lang(uid)
        t = TEXTS[lang]
        text = msg.text

        if text == t["withdraw"]:
            users_waiting[uid] = WITHDRAW_THREAD
            await msg.answer(t["withdraw_msg"])
            return

        if text == t["payment"]:
            users_waiting[uid] = NO_ACCOUNT_THREAD
            await msg.answer(t["payment_msg"])
            return

        if text == t["tech"]:
            users_waiting[uid] = TECH_THREAD
            await msg.answer(t["tech_msg"])
            return

        if text == t["back"]:
            await msg.answer(t["menu"])
            return

        # forward message
        if uid in users_waiting:
            thread = users_waiting.pop(uid)

            await msg.bot.send_message(
                GROUP_ID,
                f"👤 {msg.from_user.full_name}\n🆔 {uid}\n\n{text}",
                message_thread_id=thread
            )

            await msg.answer("✅ Sent")