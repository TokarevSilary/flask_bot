from create_table.create_session import db
from app import app
from sqlalchemy import inspect

with app.app_context():
    from create_table import base_information  # импорт моделей **только здесь**, внутри контекста
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Таблицы в базе данных:")
    for table in tables:
        print("-", table)