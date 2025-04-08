from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from aiogram.exceptions import TelegramBadRequest
from app.models import Persons, async_session

from app.utils import valid_fio
import app.keyboards as kb
import app.requests as req

router = Router()

class Form(StatesGroup):
    fio = State()
    gender = State()
    birth_date = State()
    death_date = State()
    bio = State()
    search = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать!', reply_markup=kb.main)


@router.message(F.text == 'Сбросить все')
async def reset_all(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Все действия отменены.")


@router.message(F.text == 'Вставить данные')
async def insert_data(message: Message, state: FSMContext):
    await message.answer("Напишите ФИО (Фамилия Имя Отчество)")
    await state.set_state(Form.fio)


@router.message(Form.fio)
async def process_fio(message: Message, state: FSMContext):
    try:
        valid_fio(message.text)
        await state.update_data(fio=message.text)
        await message.answer("Напишите пол ('Мужской' или 'Женский')")
        await state.set_state(Form.gender)
    except TypeError as e:
        await message.answer(str(e))


@router.message(Form.gender)
async def process_gender(message: Message, state: FSMContext):
    gender = message.text.strip().capitalize()
    if gender not in ["Мужской", "Женский"]:
        await message.answer("Пожалуйста, укажите пол как 'Мужской' или 'Женский'")
        return
    await state.update_data(gender=gender)
    await message.answer("Укажите дату рождения в формате ДД.ММ.ГГГГ")
    await state.set_state(Form.birth_date)


@router.message(Form.birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        await state.update_data(birth_date=birth_date)
        await message.answer("Укажите дату смерти (ДД.ММ.ГГГГ) или 'нет'")
        await state.set_state(Form.death_date)
    except ValueError:
        await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ")


@router.message(Form.death_date)
async def process_death_date(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    death_date = None
    if text != "нет":
        try:
            death_date = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer("Неверный формат. Введите дату или 'нет'")
            return
    await state.update_data(death_date=death_date)
    await message.answer("Напишите биографию или 'нет'")
    await state.set_state(Form.bio)


@router.message(Form.bio)
async def process_bio(message: Message, state: FSMContext):
    bio = message.text if message.text.lower() != "нет" else None
    data = await state.get_data()
    fio_parts = data['fio'].split()
    last_name, first_name, father_name = fio_parts[0], fio_parts[1], fio_parts[2]
    try:
        async with async_session() as session:
            new_person = Persons(
                first_name=first_name,
                last_name=last_name,
                father_name=father_name,
                birth_date=data['birth_date'],
                death_date=data['death_date'],
                gender=data['gender'],
                bio=bio,
                photo_url=None
            )
            session.add(new_person)
            await session.commit()
            await message.answer("Данные успешно сохранены!")
    except Exception as e:
        await message.answer(f"Ошибка сохранения: {str(e)}")
    finally:
        await state.clear()


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
    response = []
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
        response.append(full_info)
    await message.answer("\n".join(response))
    await state.clear()


@router.message()
async def flood(message: Message):
    await message.answer("Выберите в меню что именно хотите сделать")