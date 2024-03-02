# <p align="center">🫐 WB Statistics Telegram Bot 🫐</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python">
  <img src="https://img.shields.io/badge/aiogram-%232671E5.svg?style=for-the-badge&logo=telegram&logoColor=white" alt="Aiogram">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/iohttp-%232C5bb4.svg?style=for-the-badge&logo=aiohttp&logoColor=white" alt="AIOHTTP">
  <img src="https://img.shields.io/badge/pydantic-E6007A?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="Postgres">
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/SQLAlchemy-529873?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white" alt="Nginx">
  <img src="https://img.shields.io/badge/uvicorn-%298729.svg?style=for-the-badge" alt="Uvicorn">
  <img src="https://img.shields.io/badge/github%20actions%20-%232671E5.svg?&style=for-the-badge&logo=github%20actions&logoColor=white"/>
</p>

___
## Описание:
Телеграм бот создан для быстрого взаимодействия с WB API.

В мобильном приложении WB Partners не реализован функционал просмотра продаж по артикулам.
Бот закрывает потребность пользователей получать более точные данные о своих продажах через мобильное
устройство.

[![Telegram](https://img.shields.io/badge/Telegram-@wb_statistics_robot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/wb_statistics_robot)

### Функционал:
⚠️ Проект находится в разработке.
- [x] Мультиаккаунт
  - [x] Добавление аккаунтов
  - [x] Редактирование аккаунтов
  - [x] Удаление аккаунтов
- [x] Сохранение токенов WB API
  - [x] Хранение организовано в зашифрованном виде по стандарту AES.
  - [x] Обновление токенов
- [x] Получение статистики
  - [x] Получение статистики артикула при выборе предустановленных периодов
  - [ ] Получение статистики при выборе произвольного периода
  - [ ] Получение статистики по нескольким артикулам за 1 запрос
- [x] Избранные запросы
  - [x] Добавление запроса в избранное
  - [x] Удаление запроса из избранного
- [x] Лимиты запросов
  - [x] Просмотр лимитов запросов
  - [x] Обновление лимитов запросов
- [ ] Уведомления
  - [ ] Уведомления о новых заказах
- [ ] Дополнительные функции.
  - [ ] Получение остатков товаров на складах
  - [ ] Получение продаж с подробным описанием

___
## Быстрый старт:
⚠️ Для полноценной работы бота необходим аккаунт WB Partners.

Последовательно выполните команды:
```
git clone https://github.com/AndreyDogadkin/wb_statistics_bot.git
```
```
cd wb_statistics_bot
```
Создайте файл .env и заполните его по примеру env.example
```
USE_PROXY=False

# Телеграм
SUPER_USERS= # list Список пользователей с неограниченными правами
TG_TOKEN=  # str Телеграм токен.
TG_TOKEN_SUPPORT=  # str -- Телеграм токен бота для отправки Админу сообщений о проблеммах
SUPPORT_ID=  # int -- id получателя сообщений о проблемах
PROXY=  # srt -- Прокси сервер

# Шифрование токенов
PASSWORD_FOR_ENCRYPTION=  # str -- Пароль для генерации ключа шифрования.
DKLEN=  # int -- Длина ключа шифрования.
ENCRYPTION_KEY= # bytes -- Ключ шифрования(сгенерировать через utils/generate_encryption_key.py)

# БД
DB_PROD= # bool -- Если False то используется SQLite
DB_HOST= # str -- Хост базы данных
DB_PORT= # int -- Порт базы занных
POSTGRES_USER= # str -- Имя пользователя
POSTGRES_PASSWORD=  # str -- Пароль базы данных.
POSTGRES_DB= # str -- Имя базы данных

# Webhook
USE_WEBHOOK= # bool -- True если используете webhook
WEBHOOK_BASE_URL= # str -- Например: https://xxx.ngrok-free.app
WEBHOOK_PATH= # str -- Например: /bot/
WEBHOOK_SECRET= # str -- Ваш секретный ключ(Придумываете/генерируете сами)
WEBHOOK_HOST= # str -- Например: http://127.0.0.1 или 0.0.0.0 если используете docker
WEBHOOK_PORT= # str -- Например: 8000
```
* Для генерации ключа шифрования, находясь в корневой директории проекта, выполните команду:
```
python bot/utils/aes_encryption/generate_encryption_key.py 
```
После заполнения, находясь в корневой директории проекта, выполните команды:
```
docker compose up
```
или
```
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m bot
```
