from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
            [KeyboardButton(text=t["pricing"])],

            [KeyboardButton(text=t["register"])],
            [KeyboardButton(text=t["trade"])],

            [KeyboardButton(text=t["problems"])],
            [KeyboardButton(text=t["admin"])],
            [KeyboardButton(text=t["lang"])]
        ],
        resize_keyboard=True
    )
# ================= THEPROP CATEGORY MENU =================
def theprop_category_kb(lang):
    t = TEXTS[lang]

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["one_step"])],
            [KeyboardButton(text=t["two_step"])],
            [KeyboardButton(text=t["funded"])],
            [KeyboardButton(text=t["back_menu"])]

        ],
        resize_keyboard=True
    )


# ================= PROBLEM MENU =================
def problem_menu(lang):
    t = TEXTS[lang]

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["withdraw"])],
            [KeyboardButton(text=t["payment"])],  # FIX: oldin no_account xato edi
            [KeyboardButton(text=t["tech"])],
            [KeyboardButton(text=t["back"])]
        ],
        resize_keyboard=True
    )


# ================= ACCOUNTS MENU =================
def theprop_accounts_kb(lang, packages):
    t = TEXTS[lang]

    rows = [packages[i:i+3] for i in range(0, len(packages), 3)]

    keyboard = [
        [KeyboardButton(text=p) for p in row]
        for row in rows
    ]

    keyboard.append([KeyboardButton(text=t["back"])])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
