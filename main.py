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
@dp.message_handler(commands=['start'], chat_type='private')
async def start(message: types.Message):
    await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)


# ================= UNIVERSAL HANDLER =================
@dp.message_handler(chat_type='private', content_types=types.ContentType.TEXT)
async def router(message: types.Message):

    uid = message.from_user.id
    text = message.text
    l = lang(uid)


    # ========= LANGUAGE =========
    if text in ["🇺🇿 O‘zbek", "🇷🇺 Русский", "🇬🇧 English"]:
        l = "uz" if "O‘zbek" in text else "ru" if "Русский" in text else "en"
        users_lang[uid] = l
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))
        return


    # ========= CHANGE =========
    if any(TEXTS[x]["change"] == text for x in TEXTS):
        await message.answer(CHOOSE_ALL, reply_markup=lang_keyboard)
        return


    # ========= ADMIN =========
    if any(TEXTS[x]["admin"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["admin_msg"], disable_web_page_preview=True)
        return


    # ========= HELP MENU =========
    if any(TEXTS[x]["help"] == text for x in TEXTS):
        await message.answer(TEXTS[l]["problem_type"], reply_markup=problem_menu(l))
        return


    # ========= WITHDRAW =========
    if any(TEXTS[x]["withdraw"] == text for x in TEXTS):
        users_thread[uid] = WITHDRAW_THREAD
        await message.answer(TEXTS[l]["login_pass"])
        return


    # ========= NO ACCOUNT =========
    if any(TEXTS[x]["no_account"] == text for x in TEXTS):
        users_thread[uid] = NO_ACCOUNT_THREAD
        await message.answer(TEXTS[l]["login_pass"])
        return


    # ========= TECH =========
    if any(TEXTS[x]["tech"] == text for x in TEXTS):
        users_thread[uid] = TECH_THREAD
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
    # =============== SEND TO GROUP (FINAL) =============
    # ==================================================
    if uid in users_thread:

        thread_id = users_thread[uid]

        profile = (
            f"https://t.me/{message.from_user.username}"
            if message.from_user.username
            else f"tg://user?id={uid}"
        )

        send_text = (
            f"📩 YANGI MUAMMO\n\n"
            f"👤 {message.from_user.full_name}\n"
            f"🔗 {profile}\n"
            f"🆔 {uid}\n\n"
            f"💬 {text}"
        )

        # guruhga yuborish
        await bot.send_message(
            GROUP_ID,
            send_text,
            message_thread_id=thread_id
        )

        # foydalanuvchiga javob
        await message.answer(TEXTS[l]["sent"])

        # 🔥 ENG MUHIM — threadni tozalaymiz (1 martalik)
        users_thread.pop(uid, None)

        # 🔥 avtomatik bosh menu
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))

        return


# ================= RUN =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)