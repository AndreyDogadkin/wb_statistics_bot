python3.11 -m venv venv
source venv/bin/activate
alembic upgrade head
python polling_main_bot.py
