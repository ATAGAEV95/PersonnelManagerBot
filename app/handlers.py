from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from app.models import Persons, async_session, Relationship, Marriage
import app.keyboards as kb
import app.requests as req
from app.utils import valid_fio, send_person_info, router as utils_router
from app.handlers_persons import router as insert_router
from app.handlers_relationships import router as relationships_router
from app.handlers_marriages import router as marriages_router


router = Router()
router.include_router(insert_router)
router.include_router(relationships_router)
router.include_router(marriages_router)
router.include_router(utils_router)


class Form(StatesGroup):
    search = State()
    edit = State()
    edit_fio = State()
    edit_birth_date = State()
    edit_death_date = State()
    edit_gender = State()
    edit_bio = State()
    edit_photo = State()


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


@router.message(F.text == 'Поиск')
async def start_search(message: Message, state: FSMContext):
    await message.answer("Введите данные для поиска:")
    await state.set_state(Form.search)


@router.message(Form.search)
async def process_fullname(message: Message, state: FSMContext):
    persons = await req.search_persons(message.text)
    if not persons:
        await message.answer("Ничего не найдено .")
        return
    for p in persons:
        full_info = f"ID: {p.person_id}\n" \
                    f"Имя: {p.first_name}\n" \
                    f"Фамилия: {p.last_name}\n" \
                    f"Отчество: {p.father_name}\n" \
                    f"Дата рождения: {p.birth_date}\n" \
                    f"Дата смерти: {p.death_date}\n" \
                    f"Пол: {p.gender}\n" \
                    f"Биография: {p.bio}\n" \
                    f"Фото: {p.photo_url}\n"
        keyboard = kb.get_edit_keyboard(p.person_id)
        await message.answer(full_info, reply_markup=keyboard)
        await state.update_data(full_info=full_info)


@router.callback_query(Form.search, F.data.startswith('edit_person_'))
async def edit_person(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split('_')[2])
    data = await state.get_data()
    full_info = data['full_info']
    await state.update_data(person_id=person_id)
    await callback.message.edit_text(full_info, reply_markup=kb.get_edit_fields_keyboard(person_id))


@router.callback_query(Form.search, F.data.startswith('back_edit_person_'))
async def back_to_edit(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split('_')[3])
    data = await state.get_data()
    full_info = data['full_info']
    await callback.message.edit_text(full_info, reply_markup=kb.get_edit_keyboard(person_id))


@router.callback_query(Form.search, F.data == 'edit_fio')
async def edit_fio(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    person_id = int(data['person_id'])
    await state.update_data(person_id=person_id)
    await callback.message.answer("Введите новое ФИО (Фамилия Имя Отчество)")
    await state.set_state(Form.edit_fio)
    await callback.answer()


@router.message(Form.edit_fio)
async def process_edit_fio(message: Message, state: FSMContext):
    data = await state.get_data()
    person_id = data['person_id']
    try:
        valid_fio(message.text)
        async with async_session() as session:
            person = await session.get(Persons, person_id)
            fio_parts = message.text.split()
            person.last_name = fio_parts[0]
            person.first_name = fio_parts[1]
            person.father_name = fio_parts[2]
            await session.commit()
        await message.answer("ФИО успешно обновлено!")
        await send_person_info(message, person_id)
        await state.set_state(Form.search)
    except TypeError as e:
        await message.answer(str(e))


# @router.callback_query(Form.search, F.data == 'edit_birth_date')
# async def edit_fio(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     person_id = int(data['person_id'])
#     await state.update_data(person_id=person_id)
#     await callback.message.answer("Введите новое ФИО (Фамилия Имя Отчество)")
#     await state.set_state(Form.edit_birth_date)
#     await callback.answer()