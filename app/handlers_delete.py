from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import app.keyboards as kb
import app.requests as req


router = Router()


class DeleteStates(StatesGroup):
    waiting_for_person_id = State()
    waiting_for_husband_id = State()
    waiting_for_wife_id = State()
    waiting_for_parent_id = State()
    waiting_for_child_id = State()


@router.message(F.text == "Удалить...")
async def process_delete_menu(message: Message):
    await message.answer("Выберите, что хотите удалить:", reply_markup=kb.delete_menu)


@router.callback_query(F.data == "delete_person")
async def delete_person_request(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DeleteStates.waiting_for_person_id)
    await callback.message.answer("Введите ID персонажа для удаления:")


@router.callback_query(F.data == "delete_couple")
async def delete_couple_request(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DeleteStates.waiting_for_husband_id)
    await callback.message.answer("Введите ID мужа для удаления связи муж-жена:")


@router.callback_query(F.data == "delete_relation")
async def delete_relation_request(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DeleteStates.waiting_for_parent_id)
    await callback.message.answer("Введите ID родителя для удаления связи родитель-ребенок:")


@router.message(DeleteStates.waiting_for_person_id)
async def process_person_id(message: Message, state: FSMContext):
    try:
        person_id = int(message.text)
        await message.answer(
            f"Вы уверены, что хотите удалить персонажа с ID {person_id}?",
            reply_markup=kb.get_delete_confirm_keyboard('person', person_id)
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID.")


@router.message(DeleteStates.waiting_for_husband_id)
async def process_husband_id(message: Message, state: FSMContext):
    try:
        husband_id = int(message.text)
        await state.update_data(husband_id=husband_id)
        await state.set_state(DeleteStates.waiting_for_wife_id)
        await message.answer("Введите ID жены для удаления связи муж-жена:")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID для мужа.")


@router.message(DeleteStates.waiting_for_wife_id)
async def process_wife_id(message: Message, state: FSMContext):
    try:
        wife_id = int(message.text)
        data = await state.get_data()
        husband_id = data.get('husband_id')
        if husband_id is None:
            await message.answer("Ошибка: ID мужа не найден. Повторите ввод.")
            await state.clear()
            return
        await message.answer(
            f"Вы уверены, что хотите удалить связь муж-жена между мужем (ID {husband_id}) и женой (ID {wife_id})?",
            reply_markup=kb.get_delete_confirm_keyboard('couple', husband_id, wife_id)
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID для жены.")


@router.message(DeleteStates.waiting_for_parent_id)
async def process_parent_id(message: Message, state: FSMContext):
    try:
        parent_id = int(message.text)
        await state.update_data(parent_id=parent_id)
        await state.set_state(DeleteStates.waiting_for_child_id)
        await message.answer("Введите ID ребенка для удаления связи родитель-ребенок:")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID для родителя.")


@router.message(DeleteStates.waiting_for_child_id)
async def process_child_id(message: Message, state: FSMContext):
    try:
        child_id = int(message.text)
        data = await state.get_data()
        parent_id = data.get('parent_id')
        if parent_id is None:
            await message.answer("Ошибка: ID родителя не найден. Повторите ввод.")
            await state.clear()
            return
        await message.answer(
            f"Вы уверены, что хотите удалить связь родитель (ID {parent_id}) - ребенок (ID {child_id})?",
            reply_markup=kb.get_delete_confirm_keyboard('relation', parent_id, child_id)
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID для ребенка.")


@router.callback_query(F.data.startswith('confirm_delete_person_'))
async def confirm_delete_person(callback: CallbackQuery):
    tokens = callback.data.split('_')
    if len(tokens) >= 4:
        person_id = int(tokens[-1])
        success, msg = await req.delete_person(person_id)
        await callback.message.answer(msg)
        await callback.answer()
    else:
        await callback.message.answer('Некорректные данные для удаления персонажа')


@router.callback_query(F.data.startswith('confirm_delete_couple_'))
async def confirm_delete_couple(callback: CallbackQuery):
    tokens = callback.data.split('_')
    if len(tokens) >= 5:
        husband_id = int(tokens[-2])
        wife_id = int(tokens[-1])
        success, msg = await req.delete_marriage(husband_id, wife_id)
        await callback.message.answer(msg)
        await callback.answer()
    else:
        await callback.message.answer('Некорректные данные для удаления связи муж-жена')


@router.callback_query(F.data.startswith('confirm_delete_relation_'))
async def confirm_delete_relation(callback: CallbackQuery):
    tokens = callback.data.split('_')
    if len(tokens) >= 5:
        parent_id = int(tokens[-2])
        child_id = int(tokens[-1])
        success, msg = await req.delete_relationship(parent_id, child_id)
        await callback.message.answer(msg)
        await callback.answer()
    else:
        await callback.message.answer('Некорректные данные для удаления связи родитель-ребенок')


@router.callback_query(F.data == "Сбросить все")
async def cancel_all(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено.")
    await callback.answer()