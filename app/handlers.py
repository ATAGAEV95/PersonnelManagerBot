from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.utils import router as utils_router
from app.handlers_persons import router as insert_router
from app.handlers_relationships import router as relationships_router
from app.handlers_marriages import router as marriages_router
from app.handlers_search import router as search_router


router = Router()
router.include_router(insert_router)
router.include_router(relationships_router)
router.include_router(marriages_router)
router.include_router(search_router)
router.include_router(utils_router)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать!', reply_markup=kb.main)


@router.message(F.text == 'Сбросить все')
async def reset_all(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Все действия отменены.")


@router.callback_query(F.data == 'Сбросить все')
async def reset_all_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Все действия отменены.")
    await callback.answer()