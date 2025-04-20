from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from app.models import Persons, async_session
from app.utils import valid_fio

router = Router()

class InsertForm(StatesGroup):
    fio = State()
    gender = State()
    birth_date = State()
    death_date = State()
    bio = State()


@router.message(F.text == 'Вставить данные')
async def insert_data(message: Message, state: FSMContext):
    await message.answer("📝 Введите ФИО (Фамилия Имя Отчество) нового человека")
    await state.set_state(InsertForm.fio)


@router.message(InsertForm.fio)
async def process_fio(message: Message, state: FSMContext):
    try:
        valid_fio(message.text)
        await state.update_data(fio=message.text)
        await message.answer("👫 Введите пол нового человека: 'Мужской' или 'Женский'")
        await state.set_state(InsertForm.gender)
    except TypeError as e:
        await message.answer(str(e))


@router.message(InsertForm.gender)
async def process_gender(message: Message, state: FSMContext):
    gender = message.text.strip().capitalize()
    if gender not in ["Мужской", "Женский"]:
        await message.answer("❌ Пожалуйста, укажите пол как 'Мужской' или 'Женский'")
        return
    await state.update_data(gender=gender)
    await message.answer("🗓 Укажите дату рождения в формате ДД.ММ.ГГГГ (например, 01.01.2000)")
    await state.set_state(InsertForm.birth_date)


@router.message(InsertForm.birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        await state.update_data(birth_date=birth_date)
        await message.answer("🗓 Укажите дату смерти в формате ДД.ММ.ГГГГ или введите 'нет', если человек жив")
        await state.set_state(InsertForm.death_date)
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ (например, 01.01.2000)")


@router.message(InsertForm.death_date)
async def process_death_date(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    death_date = None
    if text != "нет":
        try:
            death_date = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer("❌ Неверный формат. Введите дату в формате ДД.ММ.ГГГГ или 'нет', если человек жив")
            return
    await state.update_data(death_date=death_date)
    await message.answer("📝 Введите краткую биографию или интересные факты о человеке. Если информации нет, введите 'нет'")
    await state.set_state(InsertForm.bio)


@router.message(InsertForm.bio)
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
            await message.answer("✅ Данные нового человека успешно сохранены!")
    except Exception as e:
        await message.answer(f"❌ Ошибка сохранения: {str(e)}")
    finally:
        await state.clear()