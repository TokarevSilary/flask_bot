
from flask import Flask, render_template, url_for, request, session, redirect, jsonify

from datetime import datetime
from dotenv import load_dotenv
import requests as rq
import secrets
import hashlib
import base64
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


def generate_pke_key():
    code_verifier = secrets.token_urlsafe(64)
    code_verifier_bytes = code_verifier.encode('utf-8')
    sha256_hash = hashlib.sha256(code_verifier_bytes).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

@app.route('/')
def index():
    # session_state = secrets.token_urlsafe(16)
    # code_verifier, code_challenge = generate_pke_key()
    # session['code_challenge'] = code_challenge
    # session['state'] = session_state
    # session['code_verifier'] = code_verifier
    return render_template('first_page.html')


@app.route('/tap_one', methods=['GET', 'POST'])
def aut():

    # session_state = session.get('state')
    # code_challenge = session.get('code_challenge')
    # print("Code verifier:", session.get('code_verifier'))
    # print("Code challenge:", code_challenge)
    # print("State:", session_state)

    return render_template('tap_one.html')



# @app.route('/ping', methods=['GET'])
# def ping():
#     return "pong", 200

@app.route('/routes_with_methods')
def show_routes_with_methods():
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        output.append(f"{rule} -> {methods}")
    return '<br>'.join(output)


@app.route('/ping/<int:user_id>', methods=['GET', 'POST'])
def exchange(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": f"Пользователь {user_id} не найден"}), 404
    refresh_token = user.refresh_token
    client_id = os.getenv("CLIENT_ID")
    device_id = user.device_id
    session_state = secrets.token_urlsafe(16)
    session["state"] = session_state
    url = "https://id.vk.ru/oauth2/token"
    payload = {
        "grant_type" : "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "device_id": device_id,
        "state": session_state
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = rq.post(url,headers=headers ,data=payload)
    print(response.status_code)
    print(response.text)
    print(response.request.body)
    if response.status_code == 200:
        response = response.json()
        refresh_token = response.get("refresh_token")
        access_token = response.get("access_token")
        expires_in = response.get("expires_in")
        if not access_token or not refresh_token:
            return jsonify({"error": "VK не вернул новые токены", "details": response.json()}), 400

        user.refresh_token = refresh_token
        user.access_token = access_token
        user.expires_in = expires_in
        user.status = 2
        db.session.commit()
        message = f"Пользователь {user_id} добавлен"
        return jsonify({"message": message}), 200

    else:
        return jsonify({"error": "Ошибка при обмене токена", "details": response.text}), response.status_code



# user_id = id
@app.route('/vk-redirect', methods=['POST'])
def vk_callback():
    data = request.get_json()
    if request.method == 'POST' and data:
        # print("Data from frontend:", data)  # выводим сам объект
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        expires_in = data['expires_in']
        user_id = data['user_id']
        device_id = data['device_id']
        if not all([access_token, refresh_token, expires_in, user_id]):
            return jsonify({"error": "Отсутствуют обязательные поля"}), 400
        user = Users.query.filter_by(id=user_id).first()
        if user:
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.expires_in = expires_in
            user.device_id = device_id
            user.status = 1
            message = f"Обновлены данные пользователя {user_id}"
        else:
            users = Users(id=user_id,
                         date_of_key=datetime.now(),
                         expires_in=expires_in,
                         device_id=device_id,
                         access_token=access_token,
                         refresh_token=refresh_token,
                          status=1)
            db.session.add(users)
            message = f"Добавлен пользователь {user_id}"
        try:
            db.session.commit()
            return jsonify({"message": message}), 200
        except Exception as e:
            return f"При добавлении человека {user_id} произошла ошибка"
    else:
        return jsonify({"error": f"Ошибка нет данных:"}), 500

    # print("Session cookie:", request.cookies)
    # print("Code verifier in session:", session.get('code_verifier'))
    # data = request.get_json(silent=True)
    # print("Session code_verifier:", session.get('code_verifier'))
    # print("Session state:", session.get('state'))
    # print("Data from frontend:", data)
    # if session.get('state') != data['state']:
    #     return "Ошибка! Подменённый ответ", 400
    #
    # code_verifier = session.get('code_verifier')
    # if not code_verifier:
    #     print("Code verifier отсутствует!")
    #     return "Ошибка: нет code_verifier", 400
    # dat = {
    #     "grant_type": 'authorization_code',
    #     "code_verifier": code_verifier,
    #     "redirect_uri": "https://flask-bot-lu45.onrender.com/callback",
    #     "code":data['code'],
    #     "client_id": os.environ.get('CLIENT_ID'),
    #     "device_id": data.get('device_id'),
    #     "state": data.get('state')
    # }
    # response = rq.post("https://id.vk.ru/oauth2/auth",
    #                    data=dat)
    # if response.ok:
    #     token_data = response.json()
    #     print(token_data)
    # else:
    #     print(response.text)
    # return "OK"



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)