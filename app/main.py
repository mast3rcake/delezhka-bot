import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.bot.handlers import router
from app.storage.database import init_db


async def main():
    init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dp = Dispatcher()

    dp.include_router(router)

    print("Bot started...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
