from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from texts import TEXTS


# ================= LANGUAGE =================
lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="🇺🇿 O‘zbek"),
        KeyboardButton(text="🇷🇺 Русский"),
        KeyboardButton(text="🇬🇧 English")
    ]],
    resize_keyboard=True
)


# ================= MAIN MENU =================
def main_menu(lang):
    t = TEXTS[lang]

    return ReplyKeyboardMarkup(
        keyboard=[
            # 🔥 tutoriallar
            [KeyboardButton(text=t["register"])],
            [KeyboardButton(text=t["trade"])],

            # 🔥 MUAMMO ADMINdan oldin
            [KeyboardButton(text=t["help"])],

            # 🔥 admin
            [KeyboardButton(text=t["admin"])],

            # 🔥 til
            [KeyboardButton(text=t["change"])]
        ],
        resize_keyboard=True
    )


# ================= PROBLEM MENU =================
def problem_menu(lang):
    t = TEXTS[lang]

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["withdraw"])],
            [KeyboardButton(text=t["no_account"])],
            [KeyboardButton(text=t["tech"])],   # 🔥 texnik muammo
            [KeyboardButton(text=t["back"])]
        ],
        resize_keyboard=True
    )