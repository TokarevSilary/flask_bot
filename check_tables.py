from create_table.base_information import Users
from create_table.create_session import db
from app import app
from sqlalchemy import inspect, text


with app.app_context():
    from create_table import base_information  # импорт моделей **только здесь**, внутри контекста
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print("Таблицы в базе данных и их колонки:")
    # for table in tables:
    #     print(f"\nТаблица: {table}")
    #     columns = inspector.get_columns(table)
    #     for col in columns:
    #         print(f"  - {col['name']} ({col['type']}) nullable={col['nullable']}")

    # for table in tables:
        # print(f"\nТаблица: {table}")
        # # получаем колонки
        # columns = inspector.get_columns(table)
        # col_names = [col['name'] for col in columns]
        # print("Колонки:", col_names)
        #
        # # получаем первые 5 строк данных
        # query = text(f"SELECT * FROM {table} LIMIT 5")
        # result = db.session.execute(query).fetchall()
        #
        # if result:
        #     for row in result:
        #         print(dict(zip(col_names, row)))
        # else:
        #     print("Данных нет")

    user = Users.query.first()
    print(f"device_id : {user.device_id}")  # расшифрованный device_id
    print(f"refresh_token: {user.refresh_token}")
