from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from app.models import async_session, Marriage


router = Router()


class MarriageForm(StatesGroup):
    husband = State()
    wife = State()
    marr_date = State()
    marr_end = State()


@router.message(F.text == 'Создать связи муж - жена')
async def insert_marriage(message: Message, state: FSMContext):
    await message.answer(
        "💍 Для создания связи 'муж - жена' убедитесь, что вы знаете ID обоих участников. "
        "Вы можете узнать нужный ID, воспользовавшись командой «Поиск».\n\n"
        "Введите ID мужа:"
    )
    await state.set_state(MarriageForm.husband)


@router.message(MarriageForm.husband)
async def process_husband(message: Message, state: FSMContext):
    await state.update_data(husband=message.text)
    await message.answer(
        "💍 Введите ID жены:"
    )
    await state.set_state(MarriageForm.wife)


@router.message(MarriageForm.wife)
async def process_wife(message: Message, state: FSMContext):
    await state.update_data(wife=message.text)
    await message.answer(
        "🗓 Укажите дату свадьбы в формате ДД.ММ.ГГГГ или введите 'нет', если дата неизвестна:"
    )
    await state.set_state(MarriageForm.marr_date)


@router.message(MarriageForm.marr_date)
async def process_marr_date(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    marr_date = None
    if text != "нет":
        try:
            marr_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Введите дату свадьбы в формате ДД.ММ.ГГГГ или 'нет'."
            )
            return
    await state.update_data(marr_date=marr_date)
    await message.answer(
        "🗓 Укажите дату развода в формате ДД.ММ.ГГГГ или введите 'нет', если связь сохраняется или дата неизвестна:"
    )
    await state.set_state(MarriageForm.marr_end)


@router.message(MarriageForm.marr_end)
async def process_marr_end(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    marr_end = None
    if text != "нет":
        try:
            marr_end = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Введите дату развода в формате ДД.ММ.ГГГГ или 'нет'."
            )
            return
    data = await state.get_data()
    try:
        async with async_session() as session:
            new_marriage = Marriage(
                husband_id=int(data['husband']),
                wife_id=int(data['wife']),
                start_date=data['marr_date'],
                end_date=marr_end
            )
            session.add(new_marriage)
            await session.commit()
            await message.answer("✅ Связь 'муж - жена' успешно создана!")
    except Exception as e:
        await message.answer(
            f"❌ Ошибка сохранения, возможно указаны неверные ID. Проверьте данные и попробуйте еще раз.\nТехническая ошибка: {str(e)}"
        )
    finally:
        await state.clear()