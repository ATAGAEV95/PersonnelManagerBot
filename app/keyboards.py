from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Поиск')],
                                     [KeyboardButton(text='Вставить данные')],
                                     [KeyboardButton(text='Создать связи родитель - ребенок')],
                                     [KeyboardButton(text='Создать связи муж - жена')],
                                     [KeyboardButton(text='Сбросить все')]],
                           resize_keyboard=True)




