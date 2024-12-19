
from flask import Flask, request, jsonify, flash, redirect, url_for, render_template, session
from flask_cors import CORS
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from telegram import Bot
from sqlalchemy.sql import text
from telegram.error import TelegramError
import asyncio
from dotenv import load_dotenv
import os
from utils.decorators import login_required

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})  



bcrypt = Bcrypt(app)
load_dotenv()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_LINK')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["TEMPLATES_AUTO_RELOAD"] = True
db = SQLAlchemy(app)

from functools import wraps
from flask import abort

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('user_role')
            if user_role != role:
                abort(403) 
            return f(*args, **kwargs)
        return decorated_function
    return decorator

telegram_bot_token = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=telegram_bot_token)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/index')
@login_required
@role_required('user')  
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


import asyncio
from telegram.error import TelegramError
from asyncio import Semaphore
from tenacity import retry, stop_after_attempt, wait_exponential
from models import User 

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def send_telegram_message(chat_id, message, semaphore):
    """Асинхронно отправляет сообщение с повторными попытками при ошибке."""
    async with semaphore:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
        except TelegramError as te:
            logging.error(f"Ошибка при отправке сообщения Telegram ID {chat_id}: {te}")
            raise

def send_notifications_to_telegram(message):
    """Отправляет уведомления всем пользователям Telegram."""
    from models import User
    try:
        telegram_users = User.query.filter(User.telegram_id.isnot(None)).all()
        semaphore = Semaphore(10) 

        async def send_all():
            tasks = [
                send_telegram_message(user.telegram_id, message, semaphore)
                for user in telegram_users
            ]
            await asyncio.gather(*tasks)

        asyncio.run(send_all())  
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомлений: {e}")

from models import Notification, User
from flask import render_template, request, redirect, flash, url_for

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def notifications():
    if request.method == 'POST':
        message = request.form.get('message')
        if not message:
            flash('Текст уведомления не может быть пустым', 'danger')
            return redirect(url_for('notifications'))

        new_notification = Notification(message=message)
        db.session.add(new_notification)
        db.session.commit()

        send_notifications_to_telegram(message)

        flash('Уведомление успешно отправлено и сохранено!', 'success')
        return redirect(url_for('notifications'))

    notifications_list = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications_list)

@app.route('/edit')
@login_required
@role_required('admin')
def edit():
    return render_template('edit_schedule.html')

import re

def validate_password(password):
    """
    Проверяет, соответствует ли пароль требованиям:
    - Минимум 8 символов
    - Хотя бы одна буква
    - Хотя бы одна цифра
    - Хотя бы один специальный символ
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if User.query.filter_by(username=username).first():
            flash('Этот логин уже занят. Пожалуйста, выберите другой.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Этот адрес электронной почты уже используется.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Пароли не совпадают.', 'danger')
            return redirect(url_for('register'))

        if not validate_password(password):
            flash(
                'Пароль должен содержать минимум 8 символов, включая буквы, цифры и специальные символы.',
                'danger'
            )
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['login'] 
        password = request.form['password']

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash('Вы успешно вошли в систему.', 'success')
            return redirect(url_for('index') if user.role == 'user' else url_for('edit'))

        flash('Неправильный логин, email или пароль.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')
 
@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    return redirect(url_for('index'))

@app.route('/update_schedule', methods=['POST'])
@login_required
def update_schedule():
    from models import Schedule
    try:
        data = request.json
        for row in data:
            if 'id' in row and row['id']:  
                schedule = Schedule.query.get(row['id'])
                if schedule:
                    schedule.day = row['day']
                    schedule.pair = row['pair']
                    schedule.time = row['time']
                    schedule.end_time = row['end_time']
                    schedule.subject = row['subject']
                    schedule.professor = row['professor']
                    schedule.room = row['room']
            else:  
                new_schedule = Schedule(
                    day=row['day'],
                    pair=row['pair'],
                    time=row['time'],
                    end_time=row['end_time'],
                    subject=row['subject'],
                    professor=row['professor'],
                    room=row['room']
                )
                db.session.add(new_schedule)

        db.session.commit()  

        send_notifications()
        response = jsonify({'message': 'Расписание успешно обновлено'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        db.session.rollback() 
        logging.error(f"Ошибка при обновлении расписания: {e}")
        response = jsonify({'message': 'Произошла ошибка при обновлении расписания'}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/delete_schedule/<int:id>', methods=['DELETE'])
@login_required
def delete_schedule(id):
    from models import Schedule
    try:
        schedule = Schedule.query.get(id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            response = jsonify({'message': 'Пара успешно удалена'})
        else:
            response = jsonify({'message': 'Пара не найдена'}), 404

        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        db.session.rollback()  
        logging.error(f"Ошибка при удалении пары: {e}")
        response = jsonify({'message': 'Произошла ошибка при удалении пары'}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/get_schedule', methods=['GET'])
def get_schedule():
    from models import Schedule
    try:
        schedules = Schedule.query.order_by(Schedule.day, Schedule.pair).all()

        schedule = []
        for schedule_item in schedules:
            schedule.append({
                'id': schedule_item.id,
                'day': schedule_item.day,
                'pair': schedule_item.pair,
                'time': schedule_item.time,
                'end_time': schedule_item.end_time,
                'subject': schedule_item.subject,
                'professor': schedule_item.professor,
                'room': schedule_item.room
            })

        response = jsonify(schedule)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        logging.error(f"Ошибка при получении расписания: {e}")
        response = jsonify({'message': 'Произошла ошибка при получении расписания'})
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    from models import Notification
    try:
        notifications = Notification.query.order_by(Notification.created_at.desc()).all()
        notification_list = []
        for notification in notifications:
            notification_list.append({
                'message': notification.message,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        response = jsonify(notification_list)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        logging.error(f"Ошибка при получении уведомлений: {e}")
        response = jsonify({'message': 'Произошла ошибка при получении уведомлений'})
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


def send_notifications():
    try: 
        telegram_users = db.session.execute(text("SELECT telegram_id FROM users")).fetchall() 
        for user in telegram_users: 
            telegram_id = user[0]
            if telegram_id: 
                try:
                    asyncio.run( bot.send_message(chat_id=telegram_id, text="Расписание обновлено! Перейдите на сайт чтобы посмотреть новое расписание")) 
                except TelegramError as te: 
                    logging.error(f"Ошибка при отправке уведомления пользователю {telegram_id}: {te}")
    except Exception as e: logging.error(f"Ошибка при отправке уведомлений: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
