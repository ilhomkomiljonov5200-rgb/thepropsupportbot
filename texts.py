from config import ADMIN_LINK


# 🌐 language choose text
CHOOSE_ALL = "🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇬🇧 Choose language"


TEXTS = {

# =================================================
# 🇺🇿 UZBEK
# =================================================
"uz": {

    "menu": "Menu 👇",
    "choose_lang": CHOOSE_ALL,
    "problem_type": "❓ Muammo turini tanlang 👇",

    # 🔥 NEW (pricing qo‘shildi)
    "pricing": "💰 TheProp narxlari",

    # 🔥 STEP SYSTEM (QO‘SHILDI)
    "choose_category": "Kategoriyani tanlang 👇",
    "choose_account": "Account tanlang 👇",
    "one_step": "🚀 One Step",
    "two_step": "🔥 Two Step",
    "funded": "💎 Funded",

    # 🔥 NEW BACK FOR MENU (QO‘SHILDI)
    "back_menu": "⬅️ Bosh menyuga qaytish",

    # 🔥 NEW ✅ (QO‘SHILDI) + 200K FIX
    "prices_title": "Paketni tanlang 👇",
    "packages": ["💰 5K", "💰 10K", "💰 25K", "💰 50K", "💰 100K", "💰 200K"],

    "register": "📋 ThePropdan ro‘yxatdan o‘tish",
    "trade": "📊 TradeLockerga ulash va savdo qilish",
    "problems": "🛠 TheProp muammolari",
    "admin": "👨‍💻 Admin bilan bog‘lanish",
    "lang": "🌐 Tilni almashtirish",
    "back": "⬅️ Orqaga",

    "wait_ticket": "⏳ Iltimos sabr qiling, avvalgi arizangiz hali ko‘rib chiqilmoqda.",

    "withdraw": "💸 Pul yechishda muammo",
    "payment": "❌ To‘lov qildim, akkaunt berilmadi",
    "tech": "⚠️ Hisob yoki dashboard ishlamayapti / bloklangan",

    "withdraw_msg": (
        "📩 Iltimos, muammoingizni batafsil yozib qoldiring.\n"
        "🔐 TheProp dashboard login va parolini yuboring.\n"
        "⚠️ Agar 2FA mavjud bo‘lsa admin bilan bog‘laning:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "withdraw_done":
        "✅ Ariza qabul qilindi.\n⏳ 3–6 soat ichida ko‘rib chiqiladi.",

    "payment_msg": (
        "🎥 https://t.me/thepropvideo/2\n\n"
        "Videodagidek ro‘yxatdan o‘ting.\n\n"
        "🔐 TheProp dashboard login va parolini yuboring.\n"
        "⚠️ Agar 2FA mavjud bo‘lsa admin bilan bog‘laning:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "payment_done":
        "✅ Ariza yuborildi.\n⏳ 12 soat ichida ko‘rib chiqiladi.",

    "tech_msg": (
        "📩 Muammoni batafsil yozing.\n"
        "🔐 TheProp dashboard login va parolini yuboring.\n"
        "⚠️ Agar 2FA mavjud bo‘lsa admin bilan bog‘laning:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "tech_done":
        "✅ Ariza qabul qilindi.\n⏳ 12 soat ichida ko‘rib chiqiladi.",

    "reply_title": "📩 Javob (Ticket",
    "admin_label": "👨‍💻 Admin"
},


# =================================================
# 🇷🇺 RUSSIAN
# =================================================
"ru": {

    "menu": "Меню 👇",
    "choose_lang": CHOOSE_ALL,
    "problem_type": "❓ Выберите тип проблемы 👇",

    "pricing": "💰 Цены TheProp",

    # 🔥 STEP SYSTEM (QO‘SHILDI)
    "choose_category": "Выберите категорию 👇",
    "choose_account": "Выберите аккаунт 👇",
    "one_step": "🚀 One Step",
    "two_step": "🔥 Two Step",
    "funded": "💎 Funded",

    # 🔥 NEW BACK FOR MENU (QO‘SHILDI)
    "back_menu": "⬅️ В меню",

    # 🔥 NEW ✅ (QO‘SHILDI) + 200K FIX
    "prices_title": "Выберите пакет 👇",
    "packages": ["💰 5K", "💰 10K", "💰 25K", "💰 50K", "💰 100K", "💰 200K"],

    "wait_ticket": "⏳ Пожалуйста подождите, предыдущая заявка ещё рассматривается.",

    "register": "📋 Регистрация через TheProp",
    "trade": "📊 Подключение к TradeLocker",
    "problems": "🛠 Проблемы TheProp",
    "admin": "👨‍💻 Связаться с админом",
    "lang": "🌐 Сменить язык",
    "back": "⬅️ Назад",

    "withdraw": "💸 Проблема с выводом",
    "payment": "❌ Оплатил, аккаунт не выдали",
    "tech": "⚠️ Дашборд/аккаунт не работает",

    "withdraw_msg": (
        "📩 Подробно опишите проблему.\n"
        "🔐 Отправьте логин и пароль Dashboard.\n"
        "⚠️ Если есть 2FA — свяжитесь с админом:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "withdraw_done":
        "✅ Заявка принята.\n⏳ Рассмотрение 3–6 часов.",

    "payment_msg": (
        "🎥 https://t.me/thepropvideo/2\n\n"
        "Зарегистрируйтесь как в видео.\n\n"
        "📩 Опишите проблему.\n"
        "🔐 Отправьте логин и пароль Dashboard.\n"
        "⚠️ Если есть 2FA — свяжитесь с админом:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "payment_done":
        "✅ Заявка отправлена.\n⏳ Рассмотрение до 12 часов.",

    "tech_msg": (
        "📩 Опишите проблему подробно.\n"
        "🔐 Отправьте логин и пароль Dashboard.\n"
        "⚠️ Если есть 2FA — свяжитесь с админом:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "tech_done":
        "✅ Заявка принята.\n⏳ Рассмотрение до 12 часов.",

    "reply_title": "📩 Ответ (Заявка",
    "admin_label": "👨‍💻 Админ"
},


# =================================================
# 🇬🇧 ENGLISH
# =================================================
"en": {

    "menu": "Menu 👇",
    "choose_lang": CHOOSE_ALL,
    "problem_type": "❓ Choose problem type 👇",

    "pricing": "💰 TheProp Prices",

    # 🔥 STEP SYSTEM (QO‘SHILDI)
    "choose_category": "Choose category 👇",
    "choose_account": "Choose account 👇",
    "one_step": "🚀 One Step",
    "two_step": "🔥 Two Step",
    "funded": "💎 Funded",

    # 🔥 NEW BACK FOR MENU (QO‘SHILDI)
    "back_menu": "⬅️ Menu",

    # 🔥 NEW ✅ (QO‘SHILDI) + 200K FIX
    "prices_title": "Choose a package 👇",
    "packages": ["💰 5K", "💰 10K", "💰 25K", "💰 50K", "💰 100K", "💰 200K"],

    "wait_ticket": "⏳ Please wait, your previous request is still being reviewed.",

    "register": "📋 Register via TheProp",
    "trade": "📊 Connect TradeLocker",
    "problems": "🛠 TheProp issues",
    "admin": "👨‍💻 Contact admin",
    "lang": "🌐 Change language",
    "back": "⬅️ Back",

    "withdraw": "💸 Withdrawal problem",
    "payment": "❌ Paid but account not received",
    "tech": "⚠️ Dashboard/account not working",

    "withdraw_msg": (
        "📩 Please describe your issue in detail.\n"
        "🔐 Send dashboard login & password.\n"
        "⚠️ If 2FA enabled contact admin:\n"
        f"👉 {ADMIN_LINK}"
    ),

    "withdraw_done":
        "✅ Request received.\n⏳ Review time: 3–6 hours.",

    "payment_msg": (
        "🎥 https://t.me/thepropvideo/2\n\n"
        "Register as shown in the video.\n\n"
        "📩 Describe your issue.\n"
        "🔐 Send login & password.\n"
        f"👉 {ADMIN_LINK}"
    ),

    "payment_done":
        "✅ Request sent.\n⏳ Review time: up to 12 hours.",

    "tech_msg": (
        "📩 Describe the issue clearly.\n"
        "🔐 Send login & password.\n"
        f"👉 {ADMIN_LINK}"
    ),

    "tech_done":
        "✅ Request received.\n⏳ Review time: up to 12 hours.",

    "reply_title": "📩 Reply (Ticket",
    "admin_label": "👨‍💻 Admin"
}
}
