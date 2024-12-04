from server import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    pair = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    professor = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(50), nullable=False)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
