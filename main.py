from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import *
from texts import TEXTS, CHOOSE_ALL
from keyboards import lang_keyboard, main_menu, problem_menu


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users_lang = {}
users_thread = {}


# ================= HELPERS =================
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


    # ==================================================
    # =============== USER → GROUP ======================
    # ==================================================
    if uid in users_thread:

        problem_type = users_thread[uid]

        # 🔥 1) HEADER
        header = (
            f"📩 YANGI MUAMMO\n\n"
            f"👤 {message.from_user.full_name}\n"
            f"🆔 {uid}\n"
            f"📂 {problem_type}"
        )

        await bot.send_message(GROUP_ID, header)

        # 🔥 2) USER MESSAGE FORWARD (reply shu yerga qilinadi)
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

    await bot.send_message(
        forwarded.id,
        f"💬 Admin:\n{message.text}"
    )


# ================= RUN =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)