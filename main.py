from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import *
from texts import TEXTS, CHOOSE_ALL
from keyboards import lang_keyboard, main_menu, problem_menu
from handlers import support


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 🔥 support handlerlarni birinchi ulaymiz (ENG MUHIM)
support.register(dp)


users_lang = {}


def lang(uid):
    return users_lang.get(uid, "uz")


# ==================================================
# ================= START ==========================
# ==================================================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)


# ==================================================
# ================= UNIVERSAL ROUTER ===============
# ==================================================
@dp.message_handler(lambda m: m.chat.type == "private")
async def router(message: types.Message):

    if not message.text:
        return

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
    if any(TEXTS[x]["change"] == text for x in TEXTS):
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return


    # ================= ADMIN LINK ==============
    if any(TEXTS[x]["admin"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["admin_msg"], disable_web_page_preview=True)
        return


    # ================= HELP BUTTON =============
    if any(TEXTS[x]["help"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["problem_type"], reply_markup=problem_menu(l))
        return


    # ================= VIDEO BUTTONS ===========
    if any(TEXTS[x]["register"] == text for x in TEXTS):
        await message.answer("🎥 https://t.me/thepropvideo/3")
        return

    if any(TEXTS[x]["trade"] == text for x in TEXTS):
        await message.answer("🎥 https://t.me/thepropvideo/4")
        return


    # ================= BACK ====================
    if any(TEXTS[x]["back"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


# ==================================================
# ================= RUN ============================
# ==================================================
if __name__ == "__main__":
    print("BOT STARTED 🚀")
    executor.start_polling(dp, skip_updates=True)