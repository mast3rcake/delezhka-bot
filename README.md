# Делёжка 🧾

Telegram-бот для разделения общих расходов.

## Возможности

- 🆕 Создание новой делёжки
- 👥 Добавление участников
- 💸 Добавление расходов
- 🧮 Автоматический расчёт долгов
- 🗑 Удаление расходов
- 📋 Просмотр всех расходов
- ✅ Inline-кнопки и удобный UX

## Технологии

- Python 3.11
- Aiogram 3
- SQLite
- Docker
- Render
- GitHub Actions ready

## Запуск локально

```bash
git clone https://github.com/mast3rcake/delezhka-bot.git

cd delezhka-bot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m app.main
```

## Docker

```bash
docker compose up --build
```

## Deploy

Проект задеплоен на Render.

## Структура проекта

```text
app/
├── bot/
├── domain/
├── storage/
└── main.py
```

## Автор

Pavel Skvortsov
