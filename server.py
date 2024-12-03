from flask import Flask, request, jsonify, send_from_directory, flash, redirect, url_for, render_template, session, abort
from flask_cors import CORS
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from telegram import Bot
from sqlalchemy.sql import text
from telegram.error import TelegramError
import asyncio

from utils.decorators import login_required

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})  

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:2505@localhost:5432/schedule'
app.config['SECRET_KEY'] = 'configure strong secret key here'

db = SQLAlchemy(app)
from dotenv import load_dotenv
import os
load_dotenv()
# Инициализация бота
telegram_bot_token = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=telegram_bot_token)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/edit')
@login_required
def edit():
    return render_template('edit_schedule.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        from models import User
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Логин уже занят. Придумайте другой логин')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Вы успешно зарегистрировались. Войдите в аккаунт')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from models import User
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id 
            return redirect(url_for('edit'))  

        flash('Неправильный логин или пароль')
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
            else:  # Вставка новой записи
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
        db.session.rollback()  # Rollback the transaction on error
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
        db.session.rollback()  # Rollback the transaction on error
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

def send_notifications():
    try: 
        telegram_users = db.session.execute(text("SELECT telegram_id FROM telegram_users")).fetchall() 
        for user in telegram_users: 
            telegram_id = user[0]
            if telegram_id: 
                try:
                    asyncio.run( bot.send_message(chat_id=telegram_id, text="Расписание обновлено! Перейдите на сайт чтобы посмотреть новое расписание")) 
                except TelegramError as te: 
                    logging.error(f"Ошибка при отправке уведомления пользователю {telegram_id}: {te}")
    except Exception as e: logging.error(f"Ошибка при отправке уведомлений: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
