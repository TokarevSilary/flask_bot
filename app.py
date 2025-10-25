
from flask import Flask, render_template, url_for, request, session, redirect

from datetime import datetime
from dotenv import load_dotenv
import requests as rq
import secrets

from sqlalchemy.orm import state
from werkzeug.exceptions import Forbidden

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
    return render_template('first_page.html')


@app.route('/tap_one', methods=['GET', 'POST'])
def aut():
    state = secrets.token_urlsafe(16)
    code_verifier = secrets.token_urlsafe(64)
    session['state'] = state
    session['code_verifier'] = code_verifier
    # Передаём в шаблон (JS)
    return render_template('tap_one.html', state=state)


@app.route('/callback', methods=['POST'])
def vk_callback():
    data = request.get_json(silent=True)
    if session.get('state') != data['state']:
        return "Ошибка! Подменённый ответ", 400

    code_verifier = session.get('code_verifier')
    dat = {
        "grant_type": 'authorization_code',
        "code_verifier": code_verifier,
        "redirect_uri": "https://flask-bot-lu45.onrender.com/callback",
        "code":data['code'],
        "client_id": os.environ.get('CLIENT_ID'),
        "device_id": data.get('device_id'),
        "state": data.get('state')
    }
    response = rq.post("https://id.vk.ru/oauth2/auth",
                       data=dat,
                       headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.ok:
        token_data = response.json()
        print(token_data)
    else:
        print(response.text)
    return "OK"



if __name__ == '__main__':
    app.run(debug=True)
