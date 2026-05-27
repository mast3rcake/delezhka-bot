from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🆕 Новая делёжка"),
                KeyboardButton(text="👥 Участники"),
            ],
            [
                KeyboardButton(text="💸 Добавить расход"),
                KeyboardButton(text="📋 Расходы"),
            ],
            [
                KeyboardButton(text="🧮 Итог"),
                KeyboardButton(text="🗑 Очистить"),
            ],
        ],
        resize_keyboard=True,
    )


def participants_keyboard(participants: list[str]) -> ReplyKeyboardMarkup:
    keyboard = []

    for participant in participants:
        keyboard.append([
            KeyboardButton(text=participant)
        ])

    keyboard.append([
        KeyboardButton(text="❌ Отмена")
    ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def participants_inline_keyboard(
    participants: list[str],
) -> InlineKeyboardMarkup:
    keyboard = []

    for participant in participants:
        keyboard.append([
            InlineKeyboardButton(
                text=participant,
                callback_data=f"payer:{participant}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="payer:cancel",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )
