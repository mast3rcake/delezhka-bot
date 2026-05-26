from decimal import Decimal, InvalidOperation

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.storage.repository import TripRepository
from app.domain.calculator import calculate_result

router = Router()


def parse_participants(text: str) -> list[str]:
    text = text.strip()

    if not text:
        return []

    if "," in text:
        parts = text.split(",")
    else:
        parts = text.split()

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def parse_add_command(text: str):
    parts = text.split(maxsplit=2)

    if len(parts) < 2:
        raise ValueError("INVALID_FORMAT")

    payer = parts[0]

    try:
        amount = Decimal(parts[1])
    except InvalidOperation:
        raise ValueError("INVALID_AMOUNT")

    if amount <= 0:
        raise ValueError("INVALID_AMOUNT")

    description = (
        parts[2]
        if len(parts) > 2
        else "Без описания"
    )

    return payer, amount, description


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я <b>Делёжка</b> 🧾\n\n"
        "Я помогу разделить расходы.\n\n"
        "Команды:\n"
        "/newtrip — новая делёжка\n"
        "/participants — добавить участников\n"
        "/add — добавить расход\n"
        "/expenses — список расходов\n"
        "/result — итог\n"
        "/clear — очистить"
    )


@router.message(Command("newtrip"))
async def newtrip_handler(message: Message):
    repository = TripRepository()
    repository.create_trip(message.chat.id)

    await message.answer(
        "Новая делёжка создана 🧾\n\n"
        "Теперь добавь участников:\n"
        "/participants Анна, Борис, Вика"
    )


@router.message(Command("participants"))
async def participants_handler(message: Message):
    repository = TripRepository()

    raw_text = message.text.replace("/participants", "").strip()
    participants = parse_participants(raw_text)

    if not participants:
        await message.answer(
            "Добавь участников.\n\n"
            "Пример:\n"
            "/participants Анна, Борис, Вика"
        )
        return

    repository.add_participants(
        message.chat.id,
        participants,
    )

    participants_text = "\n".join(
        f"{index}. {name}"
        for index, name in enumerate(participants, start=1)
    )

    await message.answer(
        "Участники добавлены ✅\n\n"
        f"{participants_text}"
    )


@router.message(Command("add"))
async def add_handler(message: Message):
    repository = TripRepository()

    raw_text = message.text.replace("/add", "").strip()

    try:
        payer, amount, description = parse_add_command(raw_text)
    except ValueError:
        await message.answer(
            "Неверный формат.\n\n"
            "Пример:\n"
            "/add Анна 1200 продукты"
        )
        return

    participants = repository.get_participants(message.chat.id)

    if payer not in participants:
        await message.answer(
            f"Участник {payer} не найден.\n\n"
            "Участники:\n"
            + "\n".join(participants)
        )
        return

    repository.add_expense(
        chat_id=message.chat.id,
        payer=payer,
        amount=amount,
        description=description,
    )

    await message.answer(
        "Расход добавлен ✅\n\n"
        f"{payer} — {amount} ₽\n"
        f"{description}"
    )
@router.message(Command("expenses"))
async def expenses_handler(message: Message):
    repository = TripRepository()

    expenses = repository.get_expenses(message.chat.id)

    if not expenses:
        await message.answer(
            "Расходов пока нет.\n\n"
            "Добавь первый:\n"
            "/add Анна 1200 продукты"
        )
        return

    total = sum(expense["amount"] for expense in expenses)

    lines = ["Расходы:\n"]

    for index, expense in enumerate(expenses, start=1):
        lines.append(
            f"{index}. {expense['payer']} — "
            f"{expense['amount']} ₽ — "
            f"{expense['description']}"
        )

    lines.append("")
    lines.append(f"Всего: {total} ₽")

    await message.answer("\n".join(lines))
@router.message(Command("result"))
async def result_handler(message: Message):
    repository = TripRepository()

    participants = repository.get_participants(
        message.chat.id
    )

    expenses = repository.get_expenses(
        message.chat.id
    )

    if not participants:
        await message.answer(
            "Нет участников.\n\n"
            "Добавь:\n"
            "/participants Анна, Борис"
        )
        return

    if not expenses:
        await message.answer(
            "Нет расходов.\n\n"
            "Добавь:\n"
            "/add Анна 1200 продукты"
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
        lines.append(
            f"{participant} — {round(amount, 2)} ₽"
        )

    lines.append("")
    lines.append("Переводы:")

    settlements = result["settlements"]

    if not settlements:
        lines.append(
            "Все уже рассчитались ✅"
        )

    else:
        for settlement in settlements:
            lines.append(
                f"{settlement['from']} → "
                f"{settlement['to']}: "
                f"{settlement['amount']} ₽"
            )

    await message.answer(
        "\n".join(lines)
    )
@router.message(Command("clear"))
async def clear_handler(message: Message):
    repository = TripRepository()

    repository.clear_trip(message.chat.id)

    await message.answer(
        "Текущая делёжка очищена ✅\n\n"
        "Создать новую:\n"
        "/newtrip"
    )
