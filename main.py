import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import *
from texts import TEXTS

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# ========= MEMORY =========
users_lang = {}
users_thread = {}
users_last_msg = {}


def lang(uid):
    return users_lang.get(uid, "uz")


# ========= START =========
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    users_lang[message.from_user.id] = "uz"
    await message.answer(TEXTS["uz"]["menu"])


# ========= PROBLEM TYPE =========
@dp.message_handler(lambda m: m.text in [
    TEXTS["uz"]["withdraw"],
    TEXTS["uz"]["no_account"],
    TEXTS["uz"]["tech"]
])
async def choose_problem(message: types.Message):
    uid = message.from_user.id
    t = TEXTS[lang(uid)]

    if message.text == t["withdraw"]:
        users_thread[uid] = WITHDRAW_THREAD

    elif message.text == t["no_account"]:
        users_thread[uid] = NO_ACCOUNT_THREAD

    else:
        users_thread[uid] = TECH_THREAD

    await message.answer(t["login_pass"])


# ========= USER SEND MESSAGE =========
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def forward_problem(message: types.Message):
    uid = message.from_user.id

    if uid not in users_thread:
        return

    thread_id = users_thread[uid]
    t = TEXTS[lang(uid)]

    caption = (
        f"📩 YANGI MUROJAAT\n\n"
        f"👤 User: {message.from_user.full_name}\n"
        f"🆔 ID: {uid}\n\n"
        f"💬 Muammo:\n{message.text or ''}"
    )

    sent = await bot.send_message(
        chat_id=GROUP_ID,
        text=caption,
        message_thread_id=thread_id   # 🔥 MUHIM
    )

    users_last_msg[uid] = sent.message_id

    await message.answer(t["sent"])


# ========= ADMIN REPLY =========
@dp.message_handler(lambda m: m.chat.id == GROUP_ID)
async def admin_reply(message: types.Message):
    if not message.reply_to_message:
        return

    text = message.reply_to_message.text

    if "ID:" not in text:
        return

    uid = int(text.split("ID: ")[1].split("\n")[0])

    await bot.send_message(
        uid,
        f"👨‍💻 Admin javobi:\n\n{message.text}",
        reply_to_message_id=users_last_msg.get(uid)
    )


# ========= RUN =========
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)