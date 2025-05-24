import hashlib

from aiogram import Router
from aiogram.types import Message

import app.keyboards as kb
from app.models import Persons, async_session

router = Router()


def hash_password(password: str) -> str:
    """Хэширует пароль с использованием SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def valid_fio(fio: str) -> None:
    """Проверяет корректность введенного ФИО (Фамилия Имя Отчество)."""
    if not isinstance(fio, str):
        raise TypeError('ФИО должна быть строкой')
    parts = fio.split()
    if len(parts) != 3:
        raise TypeError('ФИО должна содержать 3 компонента')
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя-_()'
    for part in parts:
        if len(part) < 2:
            raise TypeError('Каждый компонент ФИО должен быть длиннее 1 символа')
        if any(c.lower() not in russian_letters for c in part):
            raise TypeError('Разрешены только русские буквы')


async def get_person_info(person_id: int) -> str:
    """Получает информацию о человеке по его ID.

    Данная функция нужна чтобы возвращало информацию о человеке,
    несмотря на нажатия кнопок клавиатуры из keyboards.
    """
    async with async_session() as session:
        person = await session.get(Persons, person_id)
        if person:
            full_info = (
                f"🆔 ID: {person.person_id}\n"
                f"👤 {person.last_name} {person.first_name} {person.father_name}\n\n"
                f"📅 Дата рождения: {person.birth_date}\n"
                f"📅 Дата смерти: {person.death_date if person.death_date else 'Н/Д'}\n"
                f"👫 Пол: {person.gender}\n\n"
                f"📋 Биография:\n{person.bio if person.bio else 'Биография отсутствует'}\n"
                f"🖼 Фото: {person.photo_url}\n"
            )
            return full_info
        else:
            return "Персона не найдена"


async def send_person_info(message: Message, person_id: int):
    full_info = await get_person_info(person_id)
    keyboard = kb.get_edit_keyboard(person_id)
    await message.answer(full_info, reply_markup=keyboard)


async def edit_text_person_info(msg, person_id: int, keyboard_func):
    full_info = await get_person_info(person_id)
    await msg.edit_text(full_info, reply_markup=keyboard_func(person_id))


@router.message()
async def flood(message: Message):
    await message.answer("Выберите в меню что именно хотите сделать")