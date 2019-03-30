from flask_sqlalchemy import SQLAlchemy
from flask import *
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/tmp'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class News(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String(5000), unique=False, nullable=False)

# Здесь будут храниться логины и пароли пользователей.

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    admin = db.Column(db.Boolean, unique=False, nullable=False)  
    
# Данная таблица содержит время начала и конца контеста.
    
class Contest(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    time_start = db.Column(db.DateTime, unique=False, nullable=False)
    time_end = db.Column(db.DateTime, unique=False, nullable=False)

# Данная таблица содержит количество очков за порядковый номер задачи в контесте.
  
class Arrangement(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    contest_index = db.Column(db.Integer,
                        db.ForeignKey('contest.id'),
                        nullable=False)
    tasks = db.relationship('Contest',
                           backref=db.backref('Tasks',
                           lazy=True))    
    problem_index = db.Column(db.Integer, unique=False, nullable=False)
    points = db.Column(db.Integer, unique=False, nullable=False)
    task_id = db.Column(db.Integer, unique=False, nullable=False)    
    
# Данная таблица описывает задачу (тесты, условие).

class ProblemItself(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    statement = db.Column(db.String(5000), unique=False, nullable=False)
    public = db.Column(db.Boolean, unique=False, nullable=False)
    
# Данная таблица описывает примеры к задачам определенного ID.

class Example(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    example_in = db.Column(db.String(5000), unique=False, nullable=False)
    example_out = db.Column(db.String(5000), unique=False, nullable=False)
    task_id = db.Column(db.Integer,
                        db.ForeignKey('problem_itself.id'),
                        nullable=False)
    task = db.relationship('ProblemItself', backref='Examples', lazy=True)

# Данная таблица описывает решение задачи на определенном контесте.

class Solution(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    submission_time = db.Column(db.DateTime, unique=False, nullable=False)
    test_case = db.Column(db.Integer, unique=False, nullable=False)
    max_time = db.Column(db.Integer, unique=False, nullable=False)
    verdict = db.Column(db.String(3), unique=False, nullable=False)
    problem_id = db.Column(db.Integer, unique=False, nullable=False)
    solution_code = db.Column(db.String(64000), unique=False, nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User',
                           backref=db.backref('Solutions',
                           lazy=True))

db.create_all()