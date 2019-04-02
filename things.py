from datetime import *
from database import *
from flask_sqlalchemy import SQLAlchemy
from flask import *


def proc(arr, func):
    a = []
    for i in arr:
        if func(i): a.append(i)
    return a


def transform(runs):
    key = {"WA": '<img src="{}"> на тесте '.format(url_for('static', filename='WA.png')),
           "AC": '<img src="{}">'.format(url_for('static', filename='AC.png')),
           "TL": '<img src="{}"> на тесте '.format(url_for('static', filename='TL.png')),
           "RE": '<img src="{}"> на тесте '.format(url_for('static', filename='RE.png')),
           "T": "Выполняется на тесте ",
           "Q": "В очереди"}
    for index, run in enumerate(runs):
        runs[index].verdict = key[runs[index].verdict]
        runs[index].submission_time = str(runs[index].submission_time).split('.')[0]
        if runs[index].verdict.endswith(' '):
            runs[index].verdict += str(runs[index].test_case)
    return runs


def get_beautiful_timediff(timed):
    return str(timed).split('.')[0]


def get_beautiful_time(t):
    return str(t).split('.')[0]


LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Table:

    def __init__(self, how_many_problems, time_start, time_end, tasks):
        self.ts = time_start
        self.te = time_end
        self.width = how_many_problems
        self.table = []
        self.tasks = tasks

        
    def append(self, elem):
        self.table.append(elem)

    def do_math_please(self):

        # Добавляем в множество всех пользователей,
        # сдавших хоть одно решение по задаче во время контеста

        # Также одновременно слегка преобразуем таблицу.

        self.user_set = set()
        for index, task in enumerate(self.table):
            for run in task:
                self.user_set.add(run.user_id)

        print(self.user_set)
        print(self.tasks)

        # Строим словарь соответствующего размера

        self.ordered_solution_list = {}
        self.logins = {}
        for user_id in self.user_set:
            login = User.query.filter_by(id=user_id).first().login
            self.logins[user_id] = login
            self.ordered_solution_list[login] = [[] for _ in range(self.width)]

        print(self.ordered_solution_list)

        # Теперь заполним словарь объектами решений.

        for index, task in enumerate(self.table):
            for run in sorted(task, key=lambda run: run.submission_time):
                author = run.user_id
                login = self.logins[author]
                self.ordered_solution_list[login][index].append(run)

        print(self.ordered_solution_list)

        # И пересчитаем количество полученных очков за каждое задание.

        for login in self.ordered_solution_list:
            for index, exact_task_runs in enumerate(self.ordered_solution_list[login]):
                if not exact_task_runs:
                    self.ordered_solution_list[login][index] = Result('', '')
                    continue
                accepted_runs = proc(exact_task_runs, lambda run: run.verdict == "AC")
                if accepted_runs:
                    last_submission_time = accepted_runs[-1].submission_time
                    self.ordered_solution_list[login][index] = Result(max(0, recalc(self.ts,
                    self.te, last_submission_time, self.tasks[index].points, len(exact_task_runs) - len(accepted_runs))),
                                                                      beautify(self.ts, last_submission_time))
                else:
                    self.ordered_solution_list[login][index] = Result(-1 * len(exact_task_runs), '')

        sorted_keys = sorted(self.ordered_solution_list.keys(), key=lambda contestant:
                             sum(proc(contestant, lambda x: type(x) == int and x > 0)))

        print(self.ordered_solution_list)

        return (self.ordered_solution_list, sorted_keys)

    
class Result:

    def __init__(self, points, submission_time):
        self.points = points
        self.submission_time = submission_time

        
def recalc(ts, te, tsub, pts, runs):
    ts = (ts - datetime(1970,1,1)).total_seconds()
    te = (te - datetime(1970,1,1)).total_seconds()
    tsub = (tsub - datetime(1970,1,1)).total_seconds()
    d1 = tsub - ts
    d2 = te - ts
    mult = d1 / d2
    return int(pts * (1 - 0.5 * mult)) - runs * 50


def beautify(ts, tsub):
    ts = (ts - datetime(1970,1,1)).total_seconds()
    tsub = (tsub - datetime(1970,1,1)).total_seconds()
    d1 = int(tsub - ts) // 60
    m = d1 // 60
    return f'{str(m).rjust(2, "0")}:{str(d1 % 60).rjust(2, "0")}'

    
def announcement(title, start_time, end_time, problems, scoredist):
    return {"title": f"Анонс раунда {title}",
"content": f'''Команда координаторов портала Codehunter рада пригласить вас на новое соревнование! Раунд начнется в {get_beautiful_time(start_time)}, а на решение задач участникам будет отведено {get_beautiful_timediff(end_time - start_time)}.
Соревнование содержит {problems} заданий. Разбалловка: {"-".join(map(str, scoredist))}.
Желаем вам удачи на контесте! Успешных решений!'''}
