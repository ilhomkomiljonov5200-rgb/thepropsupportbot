import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import TOKEN
from texts import TEXTS, CHOOSE_ALL
from keyboards import lang_keyboard, main_menu, problem_menu
from handlers import support


# ==================================================
# BOT INIT
# ==================================================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔥 support handlerlar (group/ticketlar)
support.register(dp)


# ==================================================
# MEMORY
# ==================================================
users_lang = {}


def lang(uid: int):
    return users_lang.get(uid, "uz")


# ==================================================
# START (HAR DOIM ISHLAYDI)
# ==================================================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)


# ==================================================
# ROUTER (FAQAT ODDIY TEXTLAR)
# ❗ commandlarni ushlamaydi
# ==================================================
@dp.message(
    F.chat.type == "private",
    F.text,
    ~F.text.startswith("/")   # 🔥 ENG MUHIM FIX
)
async def router(message: Message):

    uid = message.from_user.id
    text = message.text
    l = lang(uid)
    t = TEXTS[l]


    # ================= LANGUAGE =================
    if text in ["🇺🇿 O‘zbek", "🇷🇺 Русский", "🇬🇧 English"]:
        l = "uz" if "O‘zbek" in text else "ru" if "Русский" in text else "en"
        users_lang[uid] = l
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ================= CHANGE LANGUAGE =========
    if text == t["change"]:
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return


    # ================= ADMIN LINK ==============
    if text == t["admin"]:
        await message.answer(t["admin_msg"], disable_web_page_preview=True)
        return


    # ================= HELP BUTTON =============
    if text == t["help"]:
        await message.answer(t["problem_type"], reply_markup=problem_menu(l))
        return


    # ================= VIDEO BUTTONS ===========
    if text == t["register"]:
        await message.answer("🎥 https://t.me/thepropvideo/3")
        return

    if text == t["trade"]:
        await message.answer("🎥 https://t.me/thepropvideo/4")
        return


    # ================= BACK ====================
    if text == t["back"]:
        await message.answer(t["menu"], reply_markup=main_menu(l))
        return


# ==================================================
# RUN
# ==================================================
async def main():
    print("BOT STARTED 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())