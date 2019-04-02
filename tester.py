import sys
import os
from time import time, sleep
import subprocess
import psutil
from threading import Thread
from database import *


TL = 2000

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def launch(test_instance, script_name, TL, stdoutput='/home/killrealm/mysite/tmp.txt'):

    g = open(stdoutput, 'w')
    start_time = time()
    p = subprocess.Popen(['python3', script_name],
                         stdout=g, stdin=open(test_instance), bufsize=-1)
    try:
        p.communicate(timeout=TL / 1000)
    except Exception:
        p.kill()
        raise TimeoutError

    end_time = time()
    g.close()
    result = open(stdoutput).read()
    return result.strip().replace('\r', ''), int(1000 * (end_time - start_time))


def check(test_instance, script_name):
    try:
        run, t = launch(test_instance, script_name, TL)
        assert run
    except TimeoutError:
        return "TL", TL
    except Exception as e:
        print(e, test_instance)
        return "RE", t
    else:
        correct_answer = open(test_instance[:-3] + '.out').read().strip()
        if run == correct_answer:
            return "AC", t
        print(run, correct_answer)
        return "WA", t


def name(t):
    n = t.split('/')[-1].split('.')[0]
    return int(n)


def test_solution(solution, calls=2):

    test_dir = os.getcwd() + f"/problem_tests/{solution.problem_id}/"
    script_name =  os.getcwd() + f"/runs/{solution.id}.py"

    tests = [os.path.join(test_dir, filename) for filename in os.listdir(test_dir)]
    tests.sort(key=name)
    test_kit = []
    for i in tests:
        if i.endswith(".in"):
            test_kit.append(i)
    i = 0
    for test_instance in test_kit:

        i += 1
        solution.verdict = "T"
        solution.test_case = i

        db.session.commit()

        test_result = check(test_instance, script_name)
        solution.max_time = max(solution.max_time, test_result[1])
        if test_result[0] in ["WA", "RE", "TL"]:
            if test_result[0] == "TL" and calls != 0:
                solution.max_time = 0
                return test_solution(solution, calls=calls-1)
            solution.verdict = test_result[0]
            solution.test_case = i
            break

    else: solution.verdict = "AC"
    db.session.commit()


def core():
    while "The best teacher in the world is WA":
        try:
            pending_solutions = Solution.query.filter_by(verdict="Q").all()
            for solution in pending_solutions:
                test_solution(solution, calls=2)
            sleep(10)
        except Exception as e:
            print(e)
            sleep(10)
            continue

core()