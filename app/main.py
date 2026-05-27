import asyncio
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.bot.handlers import router
from app.storage.database import init_db


async def healthcheck(request):
    return web.Response(text="OK")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", "8000"))

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=port,
    )

    await site.start()


async def main():
    init_db()

    await start_web_server()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("Bot started...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
