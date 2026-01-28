from aiogram import types
from config import GROUP_ID, WITHDRAW_THREAD, NO_ACCOUNT_THREAD, TECH_THREAD
from texts import TEXTS
from keyboards import main_menu
from db import add_ticket, get_user

users_thread = {}
users_last_msg = {}
users_lang = {}


def register(dp):

    def lang(uid):
        return users_lang.get(uid, "uz")


    # ========= ADMIN REPLY =========
    @dp.message_handler(lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
    async def admin_reply(message: types.Message):

        user_id = get_user(message.reply_to_message.message_id)
        if not user_id:
            return

        await message.bot.send_message(
            user_id,
            f"👨‍💻 Admin javobi:\n{message.text}",
            reply_to_message_id=users_last_msg.get(user_id)
        )


    # ========= MUAMMO TANLASH =========
    @dp.message_handler(lambda m: any(
        TEXTS[x]["withdraw"] == m.text or
        TEXTS[x]["no_account"] == m.text or
        TEXTS[x]["tech"] == m.text
        for x in TEXTS
    ))
    async def start_problem(message: types.Message):

        uid = message.from_user.id
        text = message.text

        if TEXTS["uz"]["withdraw"] == text:
            users_thread[uid] = WITHDRAW_THREAD
        elif TEXTS["uz"]["no_account"] == text:
            users_thread[uid] = NO_ACCOUNT_THREAD
        else:
            users_thread[uid] = TECH_THREAD

        await message.answer(TEXTS["uz"]["login_pass"])


    # ========= USER → GROUP =========
    @dp.message_handler(lambda m: m.from_user.id in users_thread)
    async def forward_problem(message: types.Message):

        uid = message.from_user.id
        thread_id = users_thread[uid]

        sent = await message.bot.send_message(
            chat_id=GROUP_ID,
            text=f"👤 {message.from_user.full_name}\n🆔 {uid}\n\n{message.text}",
            message_thread_id=int(thread_id)   # 🔥 MUHIM int()
        )

        add_ticket(uid, sent.message_id)
        users_last_msg[uid] = message.message_id

        await message.answer(TEXTS["uz"]["sent"])
        await message.answer(TEXTS["uz"]["menu"], reply_markup=main_menu("uz"))

        users_thread.pop(uid, None)