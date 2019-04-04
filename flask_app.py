from flask import *
import os
from loginform import LoginForm
from signupform import SignUpForm
from add_news import *
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from zipfile import ZipFile
from things import *
from api_thingies import *
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
        password = generate_password_hash(form.password.data)
        if not User.query.filter(User.login == login).first():
            # Если нет такого логина, то продолжить
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
        correct = User.query.filter(User.login == login,).first()
        if correct and (check_password_hash(correct.password, password)
                        or password == correct.password):
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
        problems_public = db.session.query(Arrangement, Contest).filter(Contest.time_end 
                                                                        < datetime.now()).all()
        problems_public.sort(key=lambda item: item.Arrangement.task_id, reverse=True)
        problems_public = [item.Arrangement.task_id for item in problems_public]
        problems = ProblemItself.query.filter((ProblemItself.id.in_(problems_public))
                                              | (ProblemItself.public.is_(True))).all()
        problems.sort(key=lambda item: item.id, reverse=True)
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
        f = open(os.getcwd() + f'/runs/{new_solution.id}.py', 'wb')
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
    if not 'username' in session:
        return redirect('/login')
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
        compressed_tests.extractall(os.getcwd() + f"/problem_tests/{new_problem.id}")


        db.session.commit()
        return redirect("/news")
    return render_template('add_problem.html', title='Добавление новости',
                           form=form)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if not 'username' in session:
        return redirect('/login')
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
    if not 'username' in session:
        return redirect('/login')
    if not session['admin']:
        return redirect("/news")
    form = AddContestForm()
    if form.validate_on_submit():
        title = form.title.data
        time_start = form.time_start.data
        time_end = form.time_end.data
        problem_ids = [int(x) for x in form.problems.data.split(',')]
        score_dist = [int(x) for x in form.score_dist.data.split(',')]
        announce = form.announce.data
        new_contest = Contest(title=title, time_start=time_start, time_end=time_end)
        for i in range(len(problem_ids)):
            new_contest.Tasks.append(Arrangement(points=score_dist[i],
                                                 problem_index=i,
                                                 task_id=problem_ids[i]))
        db.session.add(new_contest)

        if announce:
            resp = announcement(title, time_start, time_end, len(score_dist), score_dist)
            title, content = resp['title'], resp['content']
            print(title, content)
            new_item = News(title=title, content=content)
            db.session.add(new_item)

        db.session.commit()
        return redirect("/news")
    return render_template('add_contest.html', title='Добавление соревнования',
                           form=form)



@app.route('/contests', methods=['GET'])
def get_contests():
    contests = Contest.query.all()
    contests.sort(key=lambda item: item.id, reverse=True)
    return render_template('contests.html', contests=contests)


@app.route('/contests/<int:c_id>', methods=['GET'])
def solve_contest(c_id):
    if not 'username' in session:
        return redirect('/login')
    contest = Contest.query.filter_by(id=c_id).first()
    tasks = [ProblemItself.query.filter_by(id=i.task_id).first() for i in contest.Tasks]
    points = [i.points for i in contest.Tasks]
    p_ids = [i.id for i in tasks]
    print(tasks)
    if contest.time_start > datetime.now():
        time_to_launch = get_beautiful_timediff(contest.time_start - datetime.now())
        return render_template('contest.html', access="denied", time_to_launch=time_to_launch)
    runs = Solution.query.filter(Solution.user_id==session['user_id'],
                                 Solution.problem_id.in_(p_ids)).all()
    runs.sort(key=lambda item: item.submission_time, reverse=True)
    beautiful_runs = transform(runs)
    if contest.time_end < datetime.now():
        return render_template('contest.html', access="upsolve", contest=contest,
            tasks=tasks, letters=LETTERS, lt=len(tasks), runs=runs, points=points)
    return render_template('contest.html', access="active", contest=contest, tasks=tasks,
                           letters=LETTERS, lt=len(tasks), runs=runs, points=points)


@app.route('/contests/<int:c_id>/<int:p_id>', methods=['GET', 'POST'])
def solve_contest_problem(c_id, p_id):

    if not 'username' in session:
        return redirect('/login')
    contest = Contest.query.filter_by(id=c_id).first()
    problem_id = contest.Tasks[p_id - 1].task_id
    problem = ProblemItself.query.filter_by(id=problem_id).first()
    examples = problem.Examples

    if contest.time_start > datetime.now():
        time_to_launch = get_beautiful_timediff(contest.time_start - datetime.now())
        return render_template('contests.html', access="denied", time_to_launch=time_to_launch)

    else:
        form = SolveProblemForm()
        if form.validate_on_submit():
            user_id = session['user_id']
            code = form.code.data.read()
            user = User.query.filter_by(id=user_id).first()
            new_solution = Solution(test_case=0,
                                    verdict="Q",
                                    submission_time=datetime.now(),
                                    max_time=0,
                                    problem_id=problem_id,
                                    solution_code=0)
            user.Solutions.append(new_solution)
            db.session.flush()

            f = open(os.getcwd() + f'/runs/{new_solution.id}.py', 'wb')
            f.write(code)
            f.close()

            db.session.commit()
            return redirect(f'/contests/{c_id}/{p_id}')

        runs = Solution.query.filter_by(problem_id=problem_id, user_id=session['user_id']).all()
        runs.sort(key=lambda item: item.submission_time, reverse=True)
        beautiful_runs = transform(runs)
        if contest.time_end < datetime.now():
            return render_template('solve_contest_problem.html', access="upsolve",
                                   contest=contest, problem=problem, examples=examples, form=form,
                                   runs=beautiful_runs, letter=LETTERS[p_id-1])

        time_left = get_beautiful_timediff(contest.time_end - datetime.now())
        return render_template('solve_contest_problem.html', access="active", time_left=time_left,
                               contest=contest, problem=problem, examples=examples,
                               form=form, runs=beautiful_runs, letter=LETTERS[p_id-1])


@app.route('/contests/<int:c_id>/standings', methods=['GET'])
def get_standings(c_id):

    contest = Contest.query.filter_by(id=c_id).first()
    tasks = contest.Tasks
    table = Table(len(tasks), contest.time_start, contest.time_end, tasks)
    for task in tasks:
        table.append(Solution.query.filter(Solution.submission_time >= contest.time_start,
                                        Solution.submission_time <= contest.time_end,
                                        Solution.problem_id == task.task_id,).all())
    standings, keys = table.do_math_please()
    total_scores = {}
    for user in keys:
        total_scores[user] = sum([i.points for i in proc(standings[user], lambda x: x.submission_time)])
    keys.sort(key=lambda x: total_scores[x], reverse=True)
    if contest.time_start > datetime.now():
        time_to_launch = get_beautiful_timediff(contest.time_start - datetime.now())
        return render_template('contests.html', access="denied", time_to_launch=time_to_launch)
    else:
        return render_template('standings.html', standings=standings, contest=contest, lt=len(tasks),
                               letters=LETTERS, points=[task.points for task in tasks],
                               keys=keys, total=total_scores)




if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
