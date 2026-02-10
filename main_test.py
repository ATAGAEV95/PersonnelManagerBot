import sys
import asyncio
from aiogram import Bot
from config import TG_TOKEN_TEST
from app.models import init_models

async def test_bot():
    """Простой тест инициализации бота и моделей"""
    try:
        # 1. Проверяем, что токен существует
        if not TG_TOKEN_TEST:
            print("ERROR: TG_TOKEN_TEST is empty")
            return False

        # 2. Инициализируем модели
        await init_models()
        print("✓ Models initialized successfully")

        # 3. Пробуем создать бота (без запуска polling)
        bot = Bot(token=TG_TOKEN_TEST)

        # 4. Проверяем соединение с Telegram
        me = await bot.get_me()
        print(f"✓ Bot connected: @{me.username} (ID: {me.id})")

        # 5. Закрываем сессию
        await bot.session.close()

        return True

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

async def main():
    success = await test_bot()
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
