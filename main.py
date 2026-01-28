import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import *
from texts import TEXTS, CHOOSE_ALL
from keyboards import lang_keyboard, main_menu, problem_menu
from handlers import support


bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔥 support handlerlarni birinchi ulaymiz
support.register(dp)


users_lang = {}


def lang(uid):
    return users_lang.get(uid, "uz")


# ==================================================
# ================= START ==========================
# ==================================================
@dp.message(CommandStart())  # ✅ 3.x uchun to‘g‘ri
async def start(message: Message):
    await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)


# ==================================================
# ================= UNIVERSAL ROUTER ===============
# ==================================================
@dp.message(F.chat.type == "private", F.text)  # ✅ faqat textlar
async def router(message: Message):

    uid = message.from_user.id
    text = message.text
    l = lang(uid)


    # ================= LANGUAGE =================
    if text in ["🇺🇿 O‘zbek", "🇷🇺 Русский", "🇬🇧 English"]:
        l = "uz" if "O‘zbek" in text else "ru" if "Русский" in text else "en"
        users_lang[uid] = l
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ================= CHANGE LANGUAGE =========
    if text == TEXTS[l]["change"]:
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return


    # ================= ADMIN LINK ==============
    if text == TEXTS[l]["admin"]:
        await message.answer(TEXTS[l]["admin_msg"], disable_web_page_preview=True)
        return


    # ================= HELP BUTTON =============
    if text == TEXTS[l]["help"]:
        await message.answer(TEXTS[l]["problem_type"], reply_markup=problem_menu(l))
        return


    # ================= VIDEO BUTTONS ===========
    if text == TEXTS[l]["register"]:
        await message.answer("🎥 https://t.me/thepropvideo/3")
        return

    if text == TEXTS[l]["trade"]:
        await message.answer("🎥 https://t.me/thepropvideo/4")
        return


    # ================= BACK ====================
    if text == TEXTS[l]["back"]:
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


# ==================================================
# ================= RUN ============================
# ==================================================
async def main():
    print("BOT STARTED 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())