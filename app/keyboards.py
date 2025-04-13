from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Поиск')],
                                     [KeyboardButton(text='Вставить данные')],
                                     [KeyboardButton(text='Создать связи родитель - ребенок')],
                                     [KeyboardButton(text='Создать связи муж - жена')],
                                     [KeyboardButton(text='Сбросить все')]],
                           resize_keyboard=True)


def get_edit_keyboard(person_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Изменить', callback_data=f'edit_person_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Выйти', callback_data='Сбросить все'))
    return keyboard.as_markup()


def get_edit_fields_keyboard(person_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Изменить ФИО', callback_data=f'edit_fio_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Изменить дату рождения', callback_data=f'edit_birth_date_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Изменить дату смерти', callback_data=f'edit_death_date_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Изменить пол', callback_data=f'edit_gender_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Изменить биографию', callback_data=f'edit_bio_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Изменить фото', callback_data=f'edit_photo_{person_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'back_edit_person_{person_id}'))
    return keyboard.adjust(1).as_markup()
