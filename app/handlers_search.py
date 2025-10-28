import os
from datetime import datetime

import paramiko
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from transliterate import translit

import app.keyboards as kb
import app.requests as req
import config as cfg
from app.models import Persons, async_session
from app.utils import edit_text_person_info, send_person_info, valid_fio

router = Router()
bot = Bot(token=cfg.TG_TOKEN)


class Form(StatesGroup):
    search = State()
    edit = State()
    edit_fio = State()
    edit_birth_date = State()
    edit_death_date = State()
    edit_gender = State()
    edit_bio = State()
    edit_photo = State()


@router.message(F.text == "Поиск")
async def start_search(message: Message, state: FSMContext):
    await message.answer(
        "🔍 Введите имя или фамилию человека, которого хотите найти.\n"
        "Можно ввести полное имя и фамилию для точного поиска."
    )
    await state.set_state(Form.search)


@router.message(Form.search)
async def process_fullname(message: Message, state: FSMContext):
    persons = await req.search_persons(message.text)
    if not persons:
        await message.answer(
            "🙁 По вашему запросу ничего не найдено. Попробуйте изменить запрос или проверить правильность написания имени/фамилии."
        )
        return
    for p in persons:
        full_info = (
            f"🆔 ID: {p.person_id}\n"
            f"👤 {p.last_name} {p.first_name} {p.father_name}\n\n"
            f"📅 Дата рождения: {p.birth_date}\n"
            f"📅 Дата смерти: {p.death_date if p.death_date else 'Н/Д'}\n"
            f"👫 Пол: {p.gender}\n\n"
            f"📋 Биография:\n{p.bio if p.bio else 'Биография отсутствует'}\n"
            f"🖼 Фото: {p.photo_url}\n"
        )
        keyboard = kb.get_edit_keyboard(p.person_id)
        await message.answer(full_info, reply_markup=keyboard)
        await state.update_data(full_info=full_info, person_id=p.person_id)


@router.callback_query(Form.search, F.data.startswith("edit_person_"))
async def edit_person(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await edit_text_person_info(callback.message, person_id, kb.get_edit_fields_keyboard)


@router.callback_query(Form.search, F.data.startswith("back_edit_person_"))
async def back_to_edit(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await edit_text_person_info(callback.message, person_id, kb.get_edit_keyboard)


@router.callback_query(Form.search, F.data.startswith("edit_fio_"))
async def edit_fio(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await callback.message.answer("✏️ Введите новое ФИО в формате: Фамилия Имя Отчество")
    await state.set_state(Form.edit_fio)
    await callback.answer()


@router.message(Form.edit_fio)
async def process_edit_fio(message: Message, state: FSMContext):
    data = await state.get_data()
    person_id = data["person_id"]
    try:
        valid_fio(message.text)
        async with async_session() as session:
            person = await session.get(Persons, person_id)
            fio_parts = message.text.split()
            person.last_name = fio_parts[0]
            person.first_name = fio_parts[1]
            person.father_name = fio_parts[2]
            await session.commit()
        await message.answer("✅ ФИО успешно обновлено!")
        await send_person_info(message, person_id)
        await state.set_state(Form.search)
    except TypeError as e:
        await message.answer(str(e))


@router.callback_query(Form.search, F.data.startswith("edit_birth_date_"))
async def edit_birth_date(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await callback.message.answer(
        "🗓 Введите новую дату рождения в формате ДД.ММ.ГГГГ (например, 01.01.2000)"
    )
    await state.set_state(Form.edit_birth_date)
    await callback.answer()


@router.message(Form.edit_birth_date)
async def process_edit_birth_date(message: Message, state: FSMContext):
    data = await state.get_data()
    person_id = data["person_id"]
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        async with async_session() as session:
            person = await session.get(Persons, person_id)
            person.birth_date = birth_date
            await session.commit()
        await message.answer("✅ Дата рождения успешно обновлена!")
        await send_person_info(message, person_id)
        await state.set_state(Form.search)
    except ValueError:
        await message.answer(
            "❌ Формат даты не распознан. Пожалуйста, используйте формат ДД.ММ.ГГГГ (например, 01.01.2000)"
        )


@router.callback_query(Form.search, F.data.startswith("edit_death_date_"))
async def edit_death_date(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await callback.message.answer(
        "🗓 Введите новую дату смерти в формате ДД.ММ.ГГГГ или напишите 'нет', если человек жив"
    )
    await state.set_state(Form.edit_death_date)
    await callback.answer()


@router.message(Form.edit_death_date)
async def process_edit_death_date(message: Message, state: FSMContext):
    data = await state.get_data()
    person_id = data["person_id"]
    text = message.text.strip().lower()
    death_date = None
    if text != "нет":
        try:
            death_date = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer(
                "❌ Неверный формат. Введите дату в формате ДД.ММ.ГГГГ или напишите 'нет'"
            )
            return
    async with async_session() as session:
        person = await session.get(Persons, person_id)
        person.death_date = death_date
        await session.commit()
    await message.answer("✅ Дата смерти успешно обновлена!")
    await send_person_info(message, person_id)
    await state.set_state(Form.search)


@router.callback_query(Form.search, F.data.startswith("edit_gender_"))
async def edit_gender(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await callback.message.answer("👫 Укажите пол: Мужской или Женский")
    await state.set_state(Form.edit_gender)
    await callback.answer()


@router.message(Form.edit_gender)
async def process_edit_gender(message: Message, state: FSMContext):
    data = await state.get_data()
    person_id = data["person_id"]
    gender = message.text.strip().capitalize()
    if gender not in ["Мужской", "Женский"]:
        await message.answer("❌ Не могу определить пол. Пожалуйста, укажите: Мужской или Женский")
        return
    async with async_session() as session:
        person = await session.get(Persons, person_id)
        person.gender = gender
        await session.commit()
    await message.answer("✅ Пол успешно обновлен!")
    await send_person_info(message, person_id)
    await state.set_state(Form.search)


@router.callback_query(Form.search, F.data.startswith("edit_bio_"))
async def edit_bio(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await callback.message.answer("📝 Введите биографию или интересные факты о человеке")
    await state.set_state(Form.edit_bio)
    await callback.answer()


@router.message(Form.edit_bio)
async def process_edit_bio(message: Message, state: FSMContext):
    data = await state.get_data()
    person_id = data["person_id"]
    bio = message.text.strip()
    async with async_session() as session:
        person = await session.get(Persons, person_id)
        person.bio = bio
        await session.commit()
    await message.answer("✅ Биография успешно сохранена!")
    await send_person_info(message, person_id)
    await state.set_state(Form.search)


@router.callback_query(Form.search, F.data.startswith("edit_photo_"))
async def edit_photo(callback: CallbackQuery, state: FSMContext):
    person_id = int(callback.data.split("_")[-1])
    await state.update_data(person_id=person_id)
    await callback.message.answer(
        "📸 Отправьте фотографию человека. Лучше всего подойдет портретное фото."
    )
    await state.set_state(Form.edit_photo)
    await callback.answer()


@router.message(Form.edit_photo, ~F.photo)
async def handle_wrong_photo_format(message: Message):
    await message.answer(
        "❌ Не вижу фотографии. Пожалуйста, отправьте изображение (не файл и не документ)"
    )


@router.message(Form.edit_photo, F.photo)
async def process_edit_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    person_id = data["person_id"]
    try:
        async with async_session() as session:
            person = await session.get(Persons, person_id)
            first_name_lat = (
                translit(person.first_name, "ru", reversed=True).lower().replace("'", "")
            )
            last_name_lat = translit(person.last_name, "ru", reversed=True).lower().replace("'", "")
            father_name_lat = (
                translit(person.father_name, "ru", reversed=True).lower().replace("'", "")
            )

            filename = f"{first_name_lat}_{last_name_lat}_{father_name_lat}.jpg"
            local_path = f"temp_{filename}"

            photo = message.photo[-1]
            file = await bot.get_file(photo.file_id)
            await bot.download_file(file.file_path, local_path)

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(cfg.SSH_HOST, cfg.SSH_PORT, cfg.SSH_USERNAME, cfg.SSH_PASSWORD)

            sftp = ssh.open_sftp()
            sftp.put(local_path, os.path.join(cfg.REMOTE_PATH, filename))
            sftp.close()
            ssh.close()

            person.photo_url = f"{cfg.BASE_URL}{filename}"
            await session.commit()

            await message.answer("✅ Фотография успешно обновлена!")
            await send_person_info(message, person_id)

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
    await state.set_state(Form.search)
