import os
from flask import Flask, abort, redirect, render_template, request, session
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

from repositories import user_repository

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('APP_SECRET_KEY')

bcrypt = Bcrypt(app)


@app.get('/')
def index():
    if 'user_id' in session:
        return redirect('/secret')
    return render_template('index.html')


@app.get('/secret')
def secret_page():
    if 'user_id' not in session:
        return redirect('/')
    user_id = session.get('user_id')
    user = user_repository.get_user_by_id(user_id)  # type: ignore
    return render_template('secret.html', user=user)


@app.post('/signup')
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        abort(400)
    does_user_exist = user_repository.does_username_exist(username)
    if does_user_exist:
        abort(400)
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_repository.create_user(username, hashed_password)
    return redirect('/')


@app.post('/login')
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        abort(400)
    user = user_repository.get_user_by_username(username)
    if user is None:
        abort(401)
    if not bcrypt.check_password_hash(user['hashed_password'], password):
        abort(401)
    session['user_id'] = user['user_id']
    return redirect('/secret')


@app.post('/logout')
def logout():
    del session['user_id']
    return redirect('/')
