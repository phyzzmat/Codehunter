from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, BooleanField, DateTimeField
from wtforms.validators import DataRequired
import datetime

 
class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')
    
class AddProblemForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired()])
    statement = TextAreaField('Условие задачи', validators=[DataRequired()], 
                              render_kw={"rows": 12, "cols": 100})
    example_in = TextAreaField('Примеры входных данных', validators=[DataRequired()], 
                              render_kw={"rows": 12, "cols": 100})
    example_out = TextAreaField('Примеры выходных данных', validators=[DataRequired()], 
                              render_kw={"rows": 12, "cols": 100})
    public = BooleanField('Приватность задачи')
    test = FileField('Тесты к задаче', validators=[DataRequired()])
    submit = SubmitField('Добавить')
    
class SolveProblemForm(FlaskForm):
    code = FileField('Ваше решение: ', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
    
class AddContestForm(FlaskForm):
    title = StringField('Название соревнования', validators=[DataRequired()])
    time_start = DateTimeField('Начало соревнования', default=datetime.datetime.now())
    time_end = DateTimeField('Окончание соревнования', default=datetime.datetime.now())
    problems = StringField('ID задач через запятую', validators=[DataRequired()])
    score_dist = StringField('Разбалловка через запятую', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
    
    