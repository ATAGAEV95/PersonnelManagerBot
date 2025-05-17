from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поиск")],
        [KeyboardButton(text="Вставить данные")],
        [KeyboardButton(text="Создать связи родитель - ребенок")],
        [KeyboardButton(text="Создать связи муж - жена")],
        [KeyboardButton(text="Удалить")],
        [KeyboardButton(text="Сбросить все")],
    ],
    resize_keyboard=True,
)


delete_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Удалить персонажа", callback_data="delete_person")],
        [InlineKeyboardButton(text="Удалить связь муж-жена", callback_data="delete_couple")],
        [
            InlineKeyboardButton(
                text="Удалить связь родитель-ребенок", callback_data="delete_relation"
            )
        ],
        [InlineKeyboardButton(text="Отмена", callback_data="Сбросить все")],
    ]
)


def get_edit_keyboard(person_id: int) -> InlineKeyboardMarkup:
    """Создаёт Inline-клавиатуру с вариантами для редактирования записи человека."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Изменить", callback_data=f"edit_person_{person_id}"))
    keyboard.add(InlineKeyboardButton(text="Выйти", callback_data="Сбросить все"))
    return keyboard.as_markup()


def get_edit_fields_keyboard(person_id: int) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру для выбора поля анкеты, которое нужно отредактировать."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✏️ Изменить ФИО", callback_data=f"edit_fio_{person_id}"))
    keyboard.add(
        InlineKeyboardButton(text="🗓 Дата рождения", callback_data=f"edit_birth_date_{person_id}")
    )
    keyboard.add(
        InlineKeyboardButton(text="🗓 Дата смерти", callback_data=f"edit_death_date_{person_id}")
    )
    keyboard.add(InlineKeyboardButton(text="👫 Пол", callback_data=f"edit_gender_{person_id}"))
    keyboard.add(InlineKeyboardButton(text="📝 Биография", callback_data=f"edit_bio_{person_id}"))
    keyboard.add(InlineKeyboardButton(text="📸 Фотография", callback_data=f"edit_photo_{person_id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_edit_person_{person_id}"))
    return keyboard.adjust(1).as_markup()


def get_delete_confirm_keyboard(entity_type: str, *args) -> InlineKeyboardMarkup:
    """Формирует Inline-клавиатуру для подтверждения удаления сущности."""
    keyboard = InlineKeyboardBuilder()

    if entity_type == "person" and len(args) == 1:
        person_id = args[0]
        keyboard.add(
            InlineKeyboardButton(
                text="Подтвердить удаление персонажа",
                callback_data=f"confirm_delete_person_{person_id}",
            )
        )
    elif entity_type == "couple" and len(args) == 2:
        husband_id, wife_id = args
        keyboard.add(
            InlineKeyboardButton(
                text="Подтвердить удаление связи муж-жена",
                callback_data=f"confirm_delete_couple_{husband_id}_{wife_id}",
            )
        )
    elif entity_type == "relation" and len(args) == 2:
        parent_id, child_id = args
        keyboard.add(
            InlineKeyboardButton(
                text="Подтвердить удаление связи родитель-ребенок",
                callback_data=f"confirm_delete_relation_{parent_id}_{child_id}",
            )
        )
    else:
        raise ValueError("Неверный тип сущности или количество аргументов")

    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="Сбросить все"))
    return keyboard.adjust(1).as_markup()
