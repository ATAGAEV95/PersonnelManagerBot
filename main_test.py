import asyncio
import sys
import time

from aiogram import Bot, Dispatcher
from config import TG_TOKEN_TEST

from app.handlers import router
from app.models import init_models


async def main():
    bot = Bot(token=TG_TOKEN_TEST)
    dp = Dispatcher()
    dp.include_router(router)
    await init_models()
    await dp.start_polling(bot)
    time.sleep(15)
    print("Test completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())