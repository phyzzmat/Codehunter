from flask import *
import os
from loginform import LoginForm
from signupform import SignUpForm
from add_news import *
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from zipfile import ZipFile
from things import transform
# from api_codehunter import *
from database import *

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found 404'}), 404)


# Главная страница платформы Codehunter. Здесь присутствует меню новостей,
# доступ к соревнованиям и логином/регистрацией.

@app.route('/')
@app.route('/index')
def index():
    # Получаем соединение с новостями и достаем все в обратном порядке
    # Отправляем обратно
    return render_template('index.html')

# Регистрация на платформе

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        login = form.username.data
        password = form.password.data
        if not User.query.filter(User.login == login).first():
            new_user = User(login=login, password=password, admin=False, rating=1e3)
            db.session.add(new_user)
            db.session.commit()
        return redirect("/index")
    return render_template('signup.html', title='Регистрация', form=form)

# Вход в систему

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.username.data
        password = form.password.data
        correct = User.query.filter(User.login == login,
                                    User.password == password).first()
        if correct:
            session['username'] = correct.login
            session['user_id'] = correct.id
            session['admin'] = correct.admin
            return redirect("/index")
        return render_template('login.html', title='Авторизация',
                               form=form, warning=True)
    return render_template('login.html', title='Авторизация',
                           form=form, warning=False)


@app.route('/logout')
def logout():
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/login')


@app.route('/news', methods=['GET'])
def get_news():
    news = News.query.all()
    print(news)
    news.sort(key=lambda item: item.id, reverse=True)
    return render_template('news.html', news=news)

@app.route('/news/<int:n_id>', methods=['GET'])
def get_news_item(n_id):
    news = News.query.filter_by(id=n_id).first()
    return render_template('news_item.html', news=news)

@app.route('/problems', methods=['GET'])
def get_problems():
    if not 'username' in session:
        return redirect('/login')
    elif session['admin']:
        problems = ProblemItself.query.all()
        return render_template('problems.html', problems=sorted(problems,
                                key=lambda item: item.id, reverse=True))
    else:
        problems_public = db.session.query(Arrangement, Contest).filter(Contest.time_end < datetime.now()).all()
        problems_public.sort(key=lambda item: item.Arrangement.task_id, reverse=True)
        problems_public = [item.Arrangement.task_id for item in problems_public]
        problems = ProblemItself.query.filter((ProblemItself.id.in_(problems_public)) | (ProblemItself.public.is_(True))).all()
    return render_template('problems.html', problems=problems)


@app.route('/problems/<int:p_id>', methods=['GET', 'POST'])
def solve_problem(p_id):
    if not 'username' in session:
        return redirect('/login')
    problem = ProblemItself.query.filter_by(id=p_id).first()
    examples = problem.Examples
    print(examples[0].example_in)
    form = SolveProblemForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        code = form.code.data.read()
        user = User.query.filter_by(id=user_id).first()
        new_solution = Solution(test_case=0,
                                verdict="Q",
                                submission_time=datetime.now(),
                                max_time=0,
                                problem_id=p_id,
                                solution_code=0)
        user.Solutions.append(new_solution)
        db.session.flush()

        print(form.code.data.read())
        f = open(os.getcwd() + f'/mysite/runs/{new_solution.id}.py', 'wb')
        f.write(code)
        f.close()

        db.session.commit()
        return redirect(f'/problems/{p_id}')
    runs = Solution.query.filter_by(problem_id=p_id, user_id=session['user_id']).all()
    runs.sort(key=lambda item: item.submission_time, reverse=True)
    beautiful_runs = transform(runs)
    return render_template('solve_problem.html', problem=problem,
                           examples=examples, form=form, runs=beautiful_runs)


@app.route('/add_problem', methods=['GET', 'POST'])
def add_problem():
    if not session['admin']:
        return redirect("/news")
    form = AddProblemForm()
    if form.validate_on_submit():
        title = form.title.data
        statement = form.statement.data
        example_in = form.example_in.data.replace("\n", "<br>").split('::')
        example_out = form.example_out.data.replace("\n", "<br>").split('::')
        private = form.public.data
        new_problem = ProblemItself(title=title, statement=statement, public=not private)
        for item in range(len(example_in)):
            new_problem.Examples.append(Example(example_in=example_in[item],
                                                example_out=example_out[item]))
        db.session.add(new_problem)
        db.session.flush()

        f = open('tmp_tests.zip', 'wb')
        f.write(form.test.data.read())
        f.close()

        compressed_tests = ZipFile("tmp_tests.zip")
        compressed_tests.extractall(os.getcwd() + f"/mysite/problem_tests/{new_problem.id}")


        db.session.commit()
        return redirect("/news")
    return render_template('add_problem.html', title='Добавление новости',
                           form=form)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if not session['admin']:
        return redirect("/news")
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_item = News(title=title, content=content)
        db.session.add(new_item)
        db.session.commit()
        return redirect("/news")
    return render_template('add_news.html', title='Добавление новости',
                           form=form)

@app.route('/add_contest', methods=['GET', 'POST'])
def add_contest():
    if not session['admin']:
        return redirect("/news")
    form = AddContestForm()
    if form.validate_on_submit():
        title = form.title.data
        time_start = form.time_start.data
        time_end = form.time_end.data
        problem_ids = [int(x) for x in form.problems.data.split(',')]
        score_dist = [int(x) for x in form.score_dist.data.split(',')]
        new_contest = Contest(title=title, time_start=time_start, time_end=time_end)
        for i in range(len(problem_ids)):
            new_contest.Tasks.append(Arrangement(points=score_dist[i],
                                                 problem_index=i,
                                                 task_id=problem_ids[i]))
        db.session.add(new_contest)
        db.session.commit()
        return redirect("/news")
    return render_template('add_contest.html', title='Добавление соревнования',
                           form=form)


@app.route('/contests', methods=['GET'])
def get_contests():
    pass


#WORK WITH NEWS-------------------------------------------------------------


#OLD EXAMPLES---------------------------------------------------------------
@app.route('/news_old')
def news():
    with open("sp.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    print(news_list)
    return render_template('news.html', news=news_list)



@app.route('/odd')
def odd_even():
    return render_template('odd_even.html', number=255)




#OLD EXAMPLES---------------------------------------------------------------

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
