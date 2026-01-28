from aiogram import types
from config import GROUP_ID
from texts import TEXTS
from keyboards import main_menu
from db import add_ticket, get_user

users_thread = {}
users_lang = {}


def register(dp):   # 🔥 MUHIM SHU QATOR

    def lang(uid):
        return users_lang.get(uid, "uz")


    # ================= ADMIN REPLY =================
    @dp.message_handler(lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
    async def admin_reply(message: types.Message):
        user_id = get_user(message.reply_to_message.message_id)
        if not user_id:
            return

        await message.bot.send_message(user_id, f"💬 Admin:\n{message.text}")


    # ================= THREAD START =================
    @dp.message_handler(lambda m: any(TEXTS[x]["withdraw"] == m.text or
                                     TEXTS[x]["no_account"] == m.text or
                                     TEXTS[x]["tech"] == m.text
                                     for x in TEXTS))
    async def start_problem(message: types.Message):
        uid = message.from_user.id
        users_thread[uid] = True
        await message.answer(TEXTS[lang(uid)]["login_pass"])


    # ================= USER → GROUP =================
    @dp.message_handler(lambda m: m.from_user.id in users_thread)
    async def forward_problem(message: types.Message):
        uid = message.from_user.id
        l = lang(uid)

        sent = await message.bot.send_message(
            GROUP_ID,
            f"👤 {message.from_user.full_name}\n🆔 {uid}\n\n{message.text}"
        )

        add_ticket(uid, sent.message_id)

        await message.answer(TEXTS[l]["sent"])
        await message.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))

        users_thread.pop(uid, None)