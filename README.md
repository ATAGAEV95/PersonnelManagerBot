# PersonnelManagerBot

**PersonnelManagerBot** — это Telegram-бот для создания записей в базу данных о ваших родственниках и друзьях, а также для администрирования информации: изменения, удаления записей и создания связей.  
Проект реализован на Python с использованием библиотеки **aiogram** и базы данных **PostgreSQL**.  
Также необходимо запустить бот [FamilyTreeBot](https://github.com/ATAGAEV95/FamilyTreeBot) для удобного просмотра информации пользователями без доступа к инструментам администрирования.

---

## Технологии

| Компонент   | Используемое решение         |
|-------------|------------------------------|
| Язык        | Python 3.10+                 |
| Библиотека  | aiogram                      |
| СУБД        | PostgreSQL                   |
| ORM         | SQLAlchemy                   |

---

## Возможности

- Добавление и просмотр информации о родственниках и друзьях
- Быстрый поиск по имени и фамилии
- Изменение или удаление существующей информации
- Поддержка нескольких Telegram-пользователей

---

## Предварительные настройки бота

Необходимо внести изменения в файл [config.py](https://github.com/ATAGAEV95/PersonnelManagerBot/blob/develop/config.py), удалив всё, и оставив только следующее:
```python
TG_TOKEN = 'Ваш токен телеграм-бота'

# Ваше подключение к БД Postgres
DATABASE_URL = "postgresql+asyncpg://login:password@host:port/bdname"

# Схема базы данных Postgres, по умолчанию "public"
SCHEMA = "public"
```
Замените `TG_TOKEN` на ваш токен телеграм-бота.  
В строке `DATABASE_URL` замените следующие параметры:  
- `login` — логин для доступа к базе данных  
- `password` — пароль для доступа к базе данных  
- `host` — хост базы данных (например, 192.168.0.1)  
- `port` — порт базы данных (обычно 5432 для Postgres)  
- `bdname` — название базы данных

Если вы планируете оставить функционал загрузки и просмотра фотографий, необходимо раскомментировать соответствующий код и указать свои параметры:
```python
# Хост и порт сервера
SSH_HOST = "192.168.0.1"
SSH_PORT = 22

# Имя пользователя и пароль
SSH_USERNAME = "root"
SSH_PASSWORD = "12345678"

# Директория на сервере, куда будут сохраняться фотографии
REMOTE_PATH = "/var/www/html/photo/"

# Адрес, по которому можно будет открыть фотографию
BASE_URL = "http://192.168.0.1/photo/"
```

Для возможности просмотра фотографий на вашем сервере Ubuntu, на котором будет запущен бот, необходимо установить Nginx:
```bash
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## Пароль для бота

Пароль необходимо указать в файле [handlers.py](https://github.com/ATAGAEV95/PersonnelManagerBot/blob/develop/app/handlers.py) в строке:
```python
ACCESS_PASSWORD = 'e5ae93bd8095fbd86c25a110bbf194a5a1a209f1e8eb31bb30c8b0ecbe254d58'
```
Данное значение представляет собой хэш-пароль, сгенерированный с использованием хэш-функции.  
Чтобы получить подобное значение, используйте функцию `hash_password`:
```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

print(hash_password('12345678'))  # ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f
```
Вы можете использовать любой свой пароль — сгенерированный хэш необходимо присвоить переменной `ACCESS_PASSWORD`.

---

## Как запустить бота

Чтобы создать Docker-образ, перейдите в корневой каталог проекта в терминале и выполните команду:
```bash
docker build . -t personnelmanagerbot
```
Для запуска контейнера Docker выполните:
```bash
docker run -d --name adminbot personnelmanagerbot
```
Для просмотра запущенных контейнеров:
```bash
docker ps
```
Чтобы остановить и, при необходимости, удалить контейнер:
```bash
docker stop adminbot
docker rm adminbot
```

---

## CI/CD

Если вы решили сделать Fork репозитория и настроить CI/CD для автоматического деплоя изменений бота, не вносите изменения в файл [config.py](https://github.com/ATAGAEV95/PersonnelManagerBot/blob/develop/config.py).  
Файл [docker-image.yml](https://github.com/ATAGAEV95/PersonnelManagerBot/blob/main/.github/workflows/docker-image.yml) содержит конфигурацию CI/CD:

Деплой бота на удалённый сервер Ubuntu осуществляется по `ssh` при выполнении `push` или `pull request` в основную ветку `main`, а также при ручном запуске в разделе Actions:
```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```
На удалённом сервере Ubuntu должен быть установлен Docker, а в домашней директории пользователя создана папка `~/deploy`:
```yaml
target: "~/deploy/"
```

Для настройки CI/CD выполните следующие шаги:  
Перейдите в раздел репозитория → `Settings` → `Secrets and variables` → `Actions` → `New repository secret` и добавьте последовательно следующие параметры:  
- `DATABASE_URL` — строка подключения в формате `"postgresql+asyncpg://login:password@host:port/bdname"`.
- `TG_TOKEN` — токен телеграм-бота (без кавычек).
- `DEPLOY_SERVER_HOST` — адрес хоста удалённого сервера Ubuntu.
- `DEPLOY_SERVER_PASSWORD` — пароль пользователя на удалённом сервере Ubuntu (например, `root`).
- `DEPLOY_SERVER_USER` — имя пользователя на удалённом сервере Ubuntu.
- `BASE_URL` — адрес для фотографий (например, "http://192.168.0.1/photo/").

---