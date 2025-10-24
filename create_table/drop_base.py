from create_table.base_information import *
from app import app


with app.app_context():
    db.drop_all()
