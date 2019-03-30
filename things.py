def transform(runs):
    key = {"WA": "Неправильный ответ на тесте ",
           "AC": "Полное решение",
           "TL": "Превышено ограничение времени на тесте ",
           "RE": "Ошибка исполнения на тесте ",
           "T": "Выполняется на тесте ",
           "Q": "В очереди"}
    for index, run in enumerate(runs):
        runs[index].verdict = key[runs[index].verdict]
        if runs[index].verdict.endswith(' '):
            runs[index].verdict += str(runs[index].test_case)
    return runs
    