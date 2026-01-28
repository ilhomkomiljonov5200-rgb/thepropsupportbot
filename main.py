from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import *
from texts import TEXTS, CHOOSE_ALL
from keyboards import lang_keyboard, main_menu, problem_menu

from db import add_ticket, get_user


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users_lang = {}
users_thread = {}


# ================= LANG =================
def lang(uid):
    return users_lang.get(uid, "uz")


# ================= START =================
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)


# ==================================================
# ================= UNIVERSAL ======================
# ==================================================
@dp.message_handler()
async def router(message: types.Message):

    if not message.text:
        return

    uid = message.from_user.id
    text = message.text
    l = lang(uid)


    # ========= LANGUAGE =========
    if text in ["🇺🇿 O‘zbek", "🇷🇺 Русский", "🇬🇧 English"]:
        l = "uz" if "O‘zbek" in text else "ru" if "Русский" in text else "en"
        users_lang[uid] = l
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ========= BUTTONS =========
    if text == TEXTS[l]["change"]:
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return

    if text == TEXTS[l]["admin"]:
        await message.answer(TEXTS[l]["admin_msg"], disable_web_page_preview=True)
        return

    if text == TEXTS[l]["help"]:
        await message.answer(TEXTS[l]["problem_type"], reply_markup=problem_menu(l))
        return


    # ========= VIDEOS =========
    if text == TEXTS[l]["register"]:
        await message.answer("🎥 https://t.me/thepropvideo/3")
        return

    if text == TEXTS[l]["trade"]:
        await message.answer("🎥 https://t.me/thepropvideo/4")
        return


    # ========= THREAD START =========
    if text in [
        TEXTS[l]["withdraw"],
        TEXTS[l]["no_account"],
        TEXTS[l]["tech"]
    ]:
        users_thread[uid] = True
        await message.answer(TEXTS[l]["login_pass"])
        return


    # ========= BACK =========
    if text == TEXTS[l]["back"]:
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ==================================================
    # =============== USER → GROUP ======================
    # ==================================================
    if uid in users_thread:

        msg = (
            f"📩 YANGI MUAMMO\n\n"
            f"👤 {message.from_user.full_name}\n"
            f"🆔 {uid}\n\n"
            f"💬 {text}"
        )

        sent = await bot.send_message(GROUP_ID, msg)

        # 🔥 ENG MUHIM JOY
        add_ticket(uid, sent.message_id)

        await message.answer(TEXTS[l]["sent"])
        users_thread.pop(uid)
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


# ==================================================
# =============== 🔥 REPLY SYSTEM ==================
# ==================================================
@dp.message_handler(lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
async def admin_reply(message: types.Message):

    user_id = get_user(message.reply_to_message.message_id)

    if not user_id:
        return

    await bot.send_message(user_id, f"💬 Admin:\n{message.text}")


# ================= RUN =================
if __name__ == "__main__":
    print("BOT STARTED 🚀")
    executor.start_polling(dp, skip_updates=True)