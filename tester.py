import sys
import os
from time import time, sleep
import subprocess
import psutil
from threading import Thread
from database import *


TL = 1000

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def launch(test_instance, script_name, TL, stdinput=subprocess.PIPE, stdoutput='/home/killrealm/mysite/tmp.txt'):

    g = open(stdoutput, 'w')
    print(test_instance, script_name, os.getcwd())
    p = subprocess.Popen(['cat', test_instance, '|',  'python3', script_name],
                         stdout=g, stdin=stdinput, bufsize=-1, shell=True)
    try:
        p.communicate(timeout=TL / 1000)
    except Exception:
        kill(p.pid)
        raise TimeoutError

    g.close()
    result = open('/home/killrealm/mysite/tmp.txt').read()
    return result.strip().replace('\r', '')


def check(test_instance, script_name):
    start_time = time()
    try:
        run = launch(test_instance, script_name, TL)
        assert run
    except TimeoutError:
        return "TL", TL
    except Exception as e:
        print(e)
        return "RE", int(1000 * (time() - start_time))
    else:
        correct_answer = open(test_instance[:-3] + '.out').read().strip()
        if run == correct_answer:
            return "AC", int(1000 * (time() - start_time))
        print(run, correct_answer)
        return "WA", int(1000 * (time() - start_time))



def test_solution(solution):

    test_dir = os.getcwd() + f"/problem_tests/{solution.problem_id}/"
    script_name =  os.getcwd() + f"/runs/{solution.id}.py"

    tests = [os.path.join(test_dir, filename) for filename in os.listdir(test_dir)]
    test_kit = []
    for i in tests:
        if i.endswith(".in"):
            test_kit.append(i)
    i = 0
    for test_instance in test_kit:

        i += 1
        solution.verdict = "T"
        solution.test_case = i
        if i % 5 == 0:
            db.session.commit()

        test_result = check(test_instance, script_name)
        solution.max_time = max(solution.max_time, test_result[1])
        if test_result[0] in ["WA", "RE", "TL"]:
            solution.verdict = test_result[0]
            solution.test_case = i
            break

    else: solution.verdict = "AC"
    db.session.commit()


def core():
    while "The best teacher in the world is WA":
        pending_solutions = Solution.query.filter_by(verdict="Q").all()
        for solution in pending_solutions:
            test_solution(solution)
        sleep(10)

core()