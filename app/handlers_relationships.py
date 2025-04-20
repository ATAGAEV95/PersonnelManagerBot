from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.models import  async_session, Relationship


router = Router()


class RelationForm(StatesGroup):
    parent = State()
    child = State()
    rel_type = State()


@router.message(F.text == 'Создать связи родитель - ребенок')
async def insert_parent(message: Message, state: FSMContext):
    await message.answer(
        "👪 Для создания связи 'родитель - ребенок' убедитесь, что вы знаете нужные ID. "
        "Если ID неизвестны, воспользуйтесь командой «Поиск» для получения информации.\n\n"
        "Введите ID родителя:"
    )
    await state.set_state(RelationForm.parent)


@router.message(RelationForm.parent)
async def process_parent(message: Message, state: FSMContext):
    await state.update_data(parent=message.text)
    await message.answer("👪 Введите ID ребенка:")
    await state.set_state(RelationForm.child)


@router.message(RelationForm.child)
async def process_child(message: Message, state: FSMContext):
    await state.update_data(child=message.text)
    await message.answer(
        "📝 Укажите степень родства. Введите один из вариантов: 'Родной', 'Приемный', 'Отчим', 'Мачеха'"
    )
    await state.set_state(RelationForm.rel_type)


@router.message(RelationForm.rel_type)
async def process_type(message: Message, state: FSMContext):
    rel_type = message.text.strip().capitalize()
    if rel_type not in ['Родной', 'Приемный', 'Отчим', 'Мачеха']:
        await message.answer("❌ Пожалуйста, введите корректный тип родства: 'Родной', 'Приемный', 'Отчим', 'Мачеха'")
        return
    data = await state.get_data()
    try:
        async with async_session() as session:
            new_relationship = Relationship(
                parent_id=int(data['parent']),
                child_id=int(data['child']),
                relationship_type=rel_type
            )
            session.add(new_relationship)
            await session.commit()
            await message.answer("✅ Связь 'родитель - ребенок' успешно создана!")
    except Exception as e:
        await message.answer(
            f"❌ Ошибка сохранения, возможно указаны неверные ID. Проверьте данные и попробуйте ещё раз.\nТехническая ошибка: {str(e)}"
        )
    finally:
        await state.clear()