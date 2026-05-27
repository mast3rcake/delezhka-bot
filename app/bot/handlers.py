from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.keyboards import (
    main_menu_keyboard,
    participants_inline_keyboard,
)
from app.bot.states import AddExpenseState, AddParticipantsState
from app.domain.calculator import calculate_result
from app.storage.repository import TripRepository


router = Router()


def parse_participants(text: str) -> list[str]:
    text = text.strip()

    if not text:
        return []

    if "," in text:
        parts = text.split(",")
    else:
        parts = text.split()

    return [part.strip() for part in parts if part.strip()]


def expense_delete_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_expense:{expense_id}",
                )
            ]
        ]
    )


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я <b>Делёжка</b> 🧾\n\n"
        "Выбери действие ниже:",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("newtrip"))
@router.message(F.text == "🆕 Новая делёжка")
async def newtrip_handler(message: Message):
    repository = TripRepository()
    repository.create_trip(message.chat.id)

    await message.answer(
        "Новая делёжка создана 🧾\n\n"
        "Теперь добавь участников кнопкой 👥 Участники",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("participants"))
async def participants_command_handler(message: Message):
    repository = TripRepository()

    raw_text = message.text.replace("/participants", "").strip()
    participants = parse_participants(raw_text)

    if not participants:
        await message.answer(
            "Добавь участников.\n\n"
            "Пример:\n"
            "/participants Анна, Борис, Вика",
            reply_markup=main_menu_keyboard(),
        )
        return

    repository.add_participants(message.chat.id, participants)

    participants_text = "\n".join(
        f"{index}. {name}"
        for index, name in enumerate(participants, start=1)
    )

    await message.answer(
        "Участники добавлены ✅\n\n"
        f"{participants_text}",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "👥 Участники")
async def participants_button_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(AddParticipantsState.waiting_for_participants)

    await message.answer(
        "Введи участников через запятую:\n\n"
        "Анна, Борис, Вика"
    )


@router.message(AddParticipantsState.waiting_for_participants)
async def participants_fsm_handler(
    message: Message,
    state: FSMContext,
):
    participants = parse_participants(message.text)

    if not participants:
        await message.answer(
            "Не вижу участников.\n\n"
            "Пример:\n"
            "Анна, Борис, Вика"
        )
        return

    repository = TripRepository()
    repository.add_participants(message.chat.id, participants)

    await state.clear()

    participants_text = "\n".join(
        f"{index}. {name}"
        for index, name in enumerate(participants, start=1)
    )

    await message.answer(
        "Участники добавлены ✅\n\n"
        f"{participants_text}",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "💸 Добавить расход")
async def add_expense_start_handler(
    message: Message,
    state: FSMContext,
):
    repository = TripRepository()
    participants = repository.get_participants(message.chat.id)

    if not participants:
        await message.answer(
            "Сначала добавь участников кнопкой 👥 Участники",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.set_state(AddExpenseState.waiting_for_payer)

    await message.answer(
        "Кто платил?",
        reply_markup=participants_inline_keyboard(participants),
    )


@router.callback_query(
    AddExpenseState.waiting_for_payer,
    F.data.startswith("payer:"),
)
async def add_expense_payer_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    payer = callback.data.replace("payer:", "")

    if payer == "cancel":
        await state.clear()

        await callback.message.answer(
            "Добавление расхода отменено.",
            reply_markup=main_menu_keyboard(),
        )

        await callback.answer()
        return

    await state.update_data(payer=payer)
    await state.set_state(AddExpenseState.waiting_for_amount)

    await callback.message.answer(
        f"Плательщик: {payer}\n\n"
        "Введите сумму расхода:\n\n"
        "Например: 1200"
    )

    await callback.answer()


@router.message(AddExpenseState.waiting_for_amount)
async def add_expense_amount_handler(
    message: Message,
    state: FSMContext,
):
    try:
        amount = Decimal(message.text.replace(",", "."))
    except InvalidOperation:
        await message.answer(
            "Сумма должна быть числом.\n\n"
            "Например: 1200"
        )
        return

    if amount <= 0:
        await message.answer("Сумма должна быть больше нуля.")
        return

    await state.update_data(amount=str(amount))
    await state.set_state(AddExpenseState.waiting_for_description)

    await message.answer(
        "Введите описание расхода:\n\n"
        "Например: продукты"
    )


@router.message(AddExpenseState.waiting_for_description)
async def add_expense_description_handler(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    payer = data["payer"]
    amount = Decimal(data["amount"])
    description = message.text.strip() or "Без описания"

    repository = TripRepository()
    repository.add_expense(
        chat_id=message.chat.id,
        payer=payer,
        amount=amount,
        description=description,
    )

    await state.clear()

    await message.answer(
        "Расход добавлен ✅\n\n"
        f"{payer} — {amount} ₽\n"
        f"{description}",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("expenses"))
@router.message(F.text == "📋 Расходы")
async def expenses_handler(message: Message):
    repository = TripRepository()
    expenses = repository.get_expenses(message.chat.id)

    if not expenses:
        await message.answer(
            "Расходов пока нет.\n\n"
            "Добавь первый через кнопку 💸 Добавить расход",
            reply_markup=main_menu_keyboard(),
        )
        return

    total = sum(expense["amount"] for expense in expenses)

    await message.answer(
        f"Расходы:\n\nВсего: {total} ₽",
        reply_markup=main_menu_keyboard(),
    )

    for index, expense in enumerate(expenses, start=1):
        await message.answer(
            f"{index}. {expense['payer']} — "
            f"{expense['amount']} ₽ — "
            f"{expense['description']}",
            reply_markup=expense_delete_keyboard(expense["id"]),
        )


@router.callback_query(F.data.startswith("delete_expense:"))
async def delete_expense_callback_handler(callback: CallbackQuery):
    expense_id = int(callback.data.replace("delete_expense:", ""))

    repository = TripRepository()
    repository.delete_expense(
        chat_id=callback.message.chat.id,
        expense_id=expense_id,
    )

    await callback.message.edit_text(
        "Расход удалён 🗑"
    )

    await callback.answer("Удалено")


@router.message(Command("result"))
@router.message(F.text == "🧮 Итог")
async def result_handler(message: Message):
    repository = TripRepository()
    participants = repository.get_participants(message.chat.id)
    expenses = repository.get_expenses(message.chat.id)

    if not participants:
        await message.answer(
            "Нет участников.\n\n"
            "Добавь их кнопкой 👥 Участники",
            reply_markup=main_menu_keyboard(),
        )
        return

    if not expenses:
        await message.answer(
            "Нет расходов.\n\n"
            "Добавь расход через кнопку 💸 Добавить расход",
            reply_markup=main_menu_keyboard(),
        )
        return

    result = calculate_result(
        participants=participants,
        expenses=expenses,
    )

    lines = [
        "Итог:\n",
        f"Общая сумма: {result['total_amount']} ₽",
        f"Доля на человека: {result['share']} ₽",
        "",
        "Кто сколько заплатил:",
    ]

    for participant, amount in result["paid"].items():
        lines.append(f"{participant} — {round(amount, 2)} ₽")

    lines.append("")
    lines.append("Переводы:")

    settlements = result["settlements"]

    if not settlements:
        lines.append("Все уже рассчитались ✅")
    else:
        for settlement in settlements:
            lines.append(
                f"{settlement['from']} → "
                f"{settlement['to']}: "
                f"{settlement['amount']} ₽"
            )

    await message.answer(
        "\n".join(lines),
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("clear"))
@router.message(F.text == "🗑 Очистить")
async def clear_handler(message: Message):
    repository = TripRepository()
    repository.clear_trip(message.chat.id)

    await message.answer(
        "Текущая делёжка очищена ✅\n\n"
        "Создать новую: 🆕 Новая делёжка",
        reply_markup=main_menu_keyboard(),
    )
