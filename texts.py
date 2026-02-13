from config import ADMIN_LINK


# 🌐 language choose text
CHOOSE_ALL = "🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇬🇧 Choose language"


TEXTS = {

# =================================================
# 🇺🇿 UZBEK
# =================================================
"uz": {

    "menu": "Menyu 👇",
    "choose_lang": CHOOSE_ALL,
    "problem_type": "❓ Muammo turini tanlang 👇",

    # 🔥 NEW (pricing qo‘shildi)
    "pricing": "💰 TheProp narxlari",

    # 🔥 STEP SYSTEM (QO‘SHILDI)
    "choose_category": "Toifani tanlang 👇",
    "choose_account": "Hisobni tanlang 👇",
    "one_step": "🚀 Bir bosqich",
    "two_step": "🔥 Ikki bosqich",
    "funded": "💎 Moliyalashtirilgan",

    # 🔥 NEW BACK FOR MENU (QO‘SHILDI)
    "back_menu": "⬅️ Bosh menyu",

    # 🔥 NEW ✅ (QO‘SHILDI) + 200K FIX
    "prices_title": "Paketni tanlang 👇",
    "packages": ["💰 5K", "💰 10K", "💰 25K", "💰 50K", "💰 100K", "💰 200K"],
    "package_selected": "✅ {package} paket tanlandi.\n\nAdmin bilan bog‘laning.",
    "challenge_label": "sinov hisobi",
    "funded_offer_label": "moliyalashtirilgan hisob",
    "fee_label": "To‘lov",
    "rules_title": "Qoidalar",
    "phase_label": "1-bosqich maqsadi",
    "phase2_label": "2-bosqich maqsadi",
    "drawdown_label": "Umumiy zarar limiti",
    "daily_drawdown_label": "Kunlik zarar limiti",
    "min_trade_days_label": "Eng kam savdo kunlari",
    "first_payout_label": "Birinchi to‘lov",
    "profit_split_label": "Foyda ulushi",
    "news_trading_label": "Yangilik paytida savdo",
    "weekend_holding_label": "Hafta oxirida pozitsiyani ushlash",
    "min_trade_days_value": "0 kun",
    "first_payout_value": "4 kun",
    "purchase_label": "Xarid qilish",

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
    "one_step": "🚀 Один этап",
    "two_step": "🔥 Два этапа",
    "funded": "💎 Финансируемый",

    # 🔥 NEW BACK FOR MENU (QO‘SHILDI)
    "back_menu": "⬅️ В меню",

    # 🔥 NEW ✅ (QO‘SHILDI) + 200K FIX
    "prices_title": "Выберите пакет 👇",
    "packages": ["💰 5K", "💰 10K", "💰 25K", "💰 50K", "💰 100K", "💰 200K"],
    "package_selected": "✅ Выбран пакет {package}.\n\nСвяжитесь с админом.",
    "challenge_label": "Челлендж",
    "funded_offer_label": "финансируемый счет",
    "fee_label": "Стоимость",
    "rules_title": "Условия",
    "phase_label": "Цель 1 этапа",
    "phase2_label": "Цель 2 этапа",
    "drawdown_label": "Общий лимит просадки",
    "daily_drawdown_label": "Дневной лимит просадки",
    "min_trade_days_label": "Мин. торговых дней",
    "first_payout_label": "Первая выплата",
    "profit_split_label": "Доля прибыли",
    "news_trading_label": "Торговля на новостях",
    "weekend_holding_label": "Удержание на выходные",
    "min_trade_days_value": "0 дней",
    "first_payout_value": "4 дня",
    "purchase_label": "Покупка",

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
    "package_selected": "✅ {package} package selected.\n\nContact admin.",
    "challenge_label": "Challenge",
    "funded_offer_label": "Funded",
    "rules_title": "Rules",
    "phase_label": "Phase 1 Target",
    "phase2_label": "Phase 2 Target",
    "drawdown_label": "Max Drawdown",
    "daily_drawdown_label": "Daily Drawdown",
    "min_trade_days_label": "Min Trading Days",
    "first_payout_label": "First Payout",
    "profit_split_label": "Profit Split",
    "news_trading_label": "News Trading",
    "weekend_holding_label": "Weekend Holding",
    "min_trade_days_value": "0 Days",
    "first_payout_value": "4 Days",
    "purchase_label": "Purchase",

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
