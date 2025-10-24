from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os

load_dotenv()
key = os.environ.get('FERNET_KEY')
if not key:
    raise ValueError("FERNET_KEY не найден!")
fernet = Fernet(key.encode())
db = SQLAlchemy()
