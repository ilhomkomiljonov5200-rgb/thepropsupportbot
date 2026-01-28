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


    # ========= CHANGE LANGUAGE =========
    if any(TEXTS[x]["change"] == text for x in TEXTS):
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return


    # ========= ADMIN LINK =========
    if any(TEXTS[x]["admin"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["admin_msg"], disable_web_page_preview=True)
        return


    # ========= HELP MENU =========
    if any(TEXTS[x]["help"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["problem_type"], reply_markup=problem_menu(l))
        return


    # ========= THREAD START =========
    if any(TEXTS[x]["withdraw"] == text for x in TEXTS) or \
       any(TEXTS[x]["no_account"] == text for x in TEXTS) or \
       any(TEXTS[x]["tech"] == text for x in TEXTS):

        users_thread[uid] = True
        await message.answer(TEXTS[l]["login_pass"])
        return


    # ========= BACK =========
    if any(TEXTS[x]["back"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ========= VIDEOS =========
    if any(TEXTS[x]["register"] == text for x in TEXTS):
        await message.answer("🎥 https://t.me/thepropvideo/3")
        return

    if any(TEXTS[x]["trade"] == text for x in TEXTS):
        await message.answer("🎥 https://t.me/thepropvideo/4")
        return


    # ==================================================
    # =============== USER → GROUP ======================
    # ==================================================
    if uid in users_thread:

        header = (
            f"📩 YANGI MUAMMO\n\n"
            f"👤 {message.from_user.full_name}\n"
            f"🆔 {uid}\n\n"
            f"💬 {text}"
        )

        sent = await bot.send_message(GROUP_ID, header)

        # 🔥 DB SAVE
        add_ticket(uid, sent.message_id)

        await message.answer(TEXTS[l]["sent"])
        users_thread.pop(uid, None)

        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


# ==================================================
# =============== 🔥 ADMIN REPLY ===================
# ==================================================
@dp.message_handler(lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
async def admin_reply(message: types.Message):

    group_msg_id = message.reply_to_message.message_id
    user_id = get_user(group_msg_id)

    if not user_id:
        return

    await bot.send_message(user_id, f"💬 Admin:\n{message.text}")


# ================= RUN =================
if __name__ == "__main__":
    print("BOT STARTED 🚀")
    executor.start_polling(dp, skip_updates=True)