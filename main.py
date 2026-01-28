from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import *
from texts import TEXTS, CHOOSE_ALL
from keyboards import lang_keyboard, main_menu, problem_menu


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
        users_lang[uid] = "uz" if "O‘zbek" in text else "ru" if "Русский" in text else "en"
        await message.answer(TEXTS[users_lang[uid]]["menu"], reply_markup=main_menu(users_lang[uid]))
        return


    # ========= CHANGE =========
    if any(TEXTS[x]["change"] == text for x in TEXTS):
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return


    # ========= ADMIN =========
    if any(TEXTS[x]["admin"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["admin_msg"], disable_web_page_preview=True)
        return


    # ========= HELP =========
    if any(TEXTS[x]["help"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["problem_type"], reply_markup=problem_menu(l))
        return


    # ========= THREAD TANLASH =========
    if any(TEXTS[x]["withdraw"] == text for x in TEXTS):
        users_thread[uid] = "Withdraw"
        await message.answer(TEXTS[l]["login_pass"])
        return

    if any(TEXTS[x]["no_account"] == text for x in TEXTS):
        users_thread[uid] = "No account"
        await message.answer(TEXTS[l]["login_pass"])
        return

    if any(TEXTS[x]["tech"] == text for x in TEXTS):
        users_thread[uid] = "Technical"
        await message.answer(TEXTS[l]["login_pass"])
        return


    # ========= VIDEOS =========
    if any(TEXTS[x]["register"] == text for x in TEXTS):
        await message.answer("🎥 https://t.me/thepropvideo/3")
        return

    if any(TEXTS[x]["trade"] == text for x in TEXTS):
        await message.answer("🎥 https://t.me/thepropvideo/4")
        return


    # ========= BACK =========
    if any(TEXTS[x]["back"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ==================================================
    # =============== USER → GROUP ======================
    # ==================================================
    if uid in users_thread:

        problem_type = users_thread[uid]

        header = (
            f"📩 YANGI MUAMMO\n\n"
            f"👤 {message.from_user.full_name}\n"
            f"🆔 {uid}\n"
            f"📂 {problem_type}"
        )

        await bot.send_message(GROUP_ID, header)
        await message.forward(GROUP_ID)

        await message.answer(TEXTS[l]["sent"])
        users_thread.pop(uid, None)
        return


# ==================================================
# =============== 🔥 REPLY SYSTEM ==================
# ==================================================
@dp.message_handler(lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
async def admin_reply(message: types.Message):

    forwarded = message.reply_to_message.forward_from

    if not forwarded:
        return

    await bot.send_message(forwarded.id, f"💬 Admin:\n{message.text}")


# ================= RUN =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)