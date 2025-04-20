from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
import app.utils as ut
import app.requests as req
from app.handlers_persons import router as insert_router
from app.handlers_relationships import router as relationships_router
from app.handlers_marriages import router as marriages_router
from app.handlers_search import router as search_router
from app.handlers_delete import router as delete_router


router = Router()
router.include_router(insert_router)
router.include_router(relationships_router)
router.include_router(marriages_router)
router.include_router(search_router)
router.include_router(delete_router)
router.include_router(ut.router)


ACCESS_PASSWORD = '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'


class RegisterState(StatesGroup):
    waiting_for_password = State()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await req.get_user_by_id(user_id)
    if user:
        await message.answer(
            "Добро пожаловать! Вы уже авторизованы.\n\n"
            "Основное меню:\n"
            "🔍 Поиск - поиск информации о человеке.\n"
            "📝 Вставить данные - добавление новой персоны.\n"
            "💍 Создать связи муж - жена - установка брачных связей между персонами.\n"
            "👪 Создать связи родитель - ребёнок - установление родственных связей между членами семьи.\n"
            "🗑 Удалить - удаление существующих данных.\n"
            "🔄 Сбросить все - отмена текущих операций и сброс состояния.\n",
            reply_markup=kb.main
        )
    else:
        await message.answer('Добро пожаловать! Для продолжения работы введите пароль для доступа.')
        await state.set_state(RegisterState.waiting_for_password)


@router.message(RegisterState.waiting_for_password)
async def password_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if ut.hash_password(message.text.strip()) == ACCESS_PASSWORD:
        await req.add_user(user_id, message.from_user.username or '')
        await message.answer(
            "Авторизация успешна! Теперь у вас полный доступ.\n\n"
            "Основное меню:\n"
            "🔍 Поиск - поиск информации о человеке.\n"
            "📝 Вставить данные - добавление новой персоны.\n"
            "💍 Создать связи муж - жена - установка брачных связей между персонами.\n"
            "👪 Создать связи родитель - ребёнок - установление родственных связей между членами семьи.\n"
            "🗑 Удалить - удаление существующих данных.\n"
            "🔄 Сбросить все - отмена текущих операций и сброс состояния.\n",
            reply_markup=kb.main
        )
        await state.clear()
    else:
        await message.answer('Неверный пароль. Попробуйте еще раз:')


@router.message(F.text == 'Сбросить все')
async def reset_all(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Все действия отменены.")


@router.callback_query(F.data == 'Сбросить все')
async def reset_all_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Все действия отменены.")
    await callback.answer()