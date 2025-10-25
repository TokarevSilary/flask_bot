
from flask import Flask, render_template, url_for, request, session, redirect

from datetime import datetime
from dotenv import load_dotenv
import requests as rq
import secrets
from create_table.create_session import db
from create_table.base_information import *
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "super secret key"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_INTERNAL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    state = secrets.token_urlsafe(16)
    session['state'] = state
    # Передаём в шаблон (JS)
    return render_template('first_page.html', state=state)


@app.route('/tap_one', methods=['GET', 'POST'])
def aut():
    return render_template('tap_one.html')


@app.route('/callback', methods=['POST'])
def vk_callback():
    data = request.get_json(silent=True)
    print(f"JSON: {data}")
    return "OK"


if __name__ == '__main__':
    app.run(debug=True)
