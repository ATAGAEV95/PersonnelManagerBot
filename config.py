# TG_TOKEN = 'Ваш токен телеграмм бота'

# Ваше подключение к БД Postgres
# DATABASE_URL = "postgresql+asyncpg://login:password@192.168.0.1:5432/bdname"

# Ваша схема из БД Postgres, по умолчанию "public"
# SCHEMA = "public"

# Ниже данные сервера где будут храниться фотографии пользователей,
# в случае если вы не будете использовать этот функционал,
# то удалите код ниже

# Хост и порт сервера
# SSH_HOST = "192.168.0.1"
# SSH_PORT = 22

# Имя пользователя и пароль
# SSH_USERNAME = "root"
# SSH_PASSWORD = "12345678"

# Директория сервера куда будут сохраняться фотографии
# REMOTE_PATH = "/var/www/html/photo/"

# Адрес по которому можно будет открыть фотографию
# BASE_URL = "http://192.168.0.1/photo/"


# Удалить код ниже если вы не используете CI/CD
import os
from dotenv import load_dotenv


load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA = "public"
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = 22
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
REMOTE_PATH = "/var/www/html/photo/"
BASE_URL = os.getenv("BASE_URL")