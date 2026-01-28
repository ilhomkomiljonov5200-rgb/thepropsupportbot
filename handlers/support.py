from aiogram.types import Message
from aiogram import F

from config import GROUP_ID, WITHDRAW_THREAD, NO_ACCOUNT_THREAD, TECH_THREAD
from texts import TEXTS
from keyboards import main_menu
from db import add_ticket, get_user


users_waiting = {}
users_last_msg = {}


def register(dp):

    # ================= ADMIN REPLY =================
    @dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
    async def admin_reply(message: Message):

        user_id = get_user(message.reply_to_message.message_id)
        if not user_id:
            return

        await message.bot.send_message(
            user_id,
            f"👨‍💻 Admin javobi:\n{message.text}",
            reply_to_message_id=users_last_msg.get(user_id)
        )


    # ================= PROBLEM BUTTON =================
    @dp.message()
    async def start_problem(message: Message):

        text = message.text
        if not text:
            return

        uid = message.from_user.id

        if any(TEXTS[x]["withdraw"] == text for x in TEXTS):
            users_waiting[uid] = WITHDRAW_THREAD

        elif any(TEXTS[x]["no_account"] == text for x in TEXTS):
            users_waiting[uid] = NO_ACCOUNT_THREAD

        elif any(TEXTS[x]["tech"] == text for x in TEXTS):
            users_waiting[uid] = TECH_THREAD

        else:
            return

        await message.answer(TEXTS["uz"]["login_pass"])


    # ================= USER → GROUP =================
    @dp.message()
    async def forward_problem(message: Message):

        uid = message.from_user.id

        if uid not in users_waiting:
            return

        thread_id = users_waiting[uid]

        sent = await message.bot.send_message(
            chat_id=GROUP_ID,
            text=f"👤 {message.from_user.full_name}\n🆔 {uid}\n\n{message.text}",
            message_thread_id=thread_id
        )

        add_ticket(uid, sent.message_id)
        users_last_msg[uid] = message.message_id

        await message.answer("✅ Yuborildi")
        users_waiting.pop(uid, None)