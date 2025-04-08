def valid_fio(fio: str):
    if not isinstance(fio, str):
        raise TypeError('ФИО должна быть строкой')

    parts = fio.split()
    if len(parts) != 3:
        raise TypeError('ФИО должна содержать 3 компонента')

    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    for part in parts:
        if len(part) < 2:
            raise TypeError('Каждый компонент ФИО должен быть длиннее 1 символа')
        if not part.isalpha():
            raise TypeError('ФИО должна содержать только буквы')
        if any(c.lower() not in russian_letters for c in part):
            raise TypeError('Разрешены только русские буквы')