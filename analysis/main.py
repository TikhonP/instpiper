from arthuranalys import HitlerClassifier
import json
import os
import requests
import time
import sys


dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, '../config.json'), 'r') as f:
    config = json.load(f)
    tokens = config['private_tokens']
    domen = config['domen']

params = {'token': tokens[0]}
url = domen+'/api/private'

main_tasks = []
main_tasks_ids = []

get_batch_delay = 5

proxypath = 'openproxy.txt'

process = 1


class Task:
    def __init__(self, task):
        self.task = task
        self.start_time = time.time()
        self.last_not_none = time.time()
    def begin(self):
        self.task_len = len(self.task['data'].split('\n'))
        self.filedata = os.path.join(
            dir_path, 'task_files/{}.txt'.format(self.task['task']))
        self.fileproxy = os.path.join(
            dir_path, 'task_files/{}_proxy.txt'.format(self.task['task']))
        with open(self.filedata, 'w') as f:
            f.write(self.task['data'])
        with open(self.fileproxy, 'w') as f:
            f.write(self.task['proxy'])
        self.hc = HitlerClassifier(self.fileproxy, self.filedata, self.task['threads'], {
                                   'is_parsed': False, 'is_id': self.task['is_id'], 'from_id': 0})
        print("STARTING HC")
        self.hc.start()

    def get_complete(self):
        print("CHECKING HOW MUCH DONE")
        complete = self.hc.how_much_done()
        print("CHECKING ALL READY ACCS")
        data = self.hc.get_all_ready_accs()
        complete = int((complete/self.task_len)*100)
        print("CHECKING IF DONE", self.hc.proxystats[0], self.hc.proxystats[1])
        if data:
            self.last_not_none = time.time()
        if (time.time() - self.last_not_none) > 60:
            complete = 100
        try:
            proxy_health = (self.hc.proxystats[0] * 100)/(self.hc.proxystats[0] + self.hc.proxystats[1])
        except ZeroDivisionError:
            proxy_health = 101
        return [complete, data, int(proxy_health)]

    def __del__(self):
        os.remove(self.fileproxy)
        os.remove(self.filedata)
        del self.hc
        print('Okay task {} removed'.format(self.task['task']))


def get_tasks():
    tasks = requests.get(url, params=params).json()
    if not tasks['status']:
        print('ERROR with request {}'.format(tasks['error']))
        return None
    if tasks['data'] == 0:
        return None
    return tasks['data']


def put_task(task):
    """task -> {"task": taskid, "data": data, "is_done": 0-100, "proxy_health": 0-101}"""
    try:
        data = json.dumps(task)
    except:
        print("\nJSON ENCODING ERROR\n\n")
        print(task)
    print(data)
    tasks = requests.put(url, params=params, data=data)
    try:
        tasks = tasks.json()
    except Exception as e:
        print('\nREQUEST ERROR "{}"\n'.format(e))
        print(tasks.text, '\n'*3)
        return 1
    if not tasks['status']:
        if tasks['error']=='deleted':
            return 2
        print('ERROR with request {}'.format(tasks['error']))
        return 1
    return None

''' Post is not supporting yet
def post_task(task):
    """task -> {"task": taskid, "data": data}"""
    tasks = requests.post(url, params=params, data=task).json()
    if not tasks['status']:
        if tasks['error']=='deleted':
            return 2
        print('ERROR with request {}'.format(tasks['error']))
        return 1
    return None
'''


def newtasks():
    tasks = get_tasks()
    if tasks is None:
        return None

    for t in tasks:
        if t['task'] in main_tasks_ids:
            continue
        print('New task! ', t)
        main_tasks.append(Task(t))
        main_tasks[len(main_tasks)-1].begin()
        main_tasks_ids.append(t['task'])


def main():
    newtasks()
    for i, t in enumerate(main_tasks):
        if (int(time.time()-t.start_time)) >= get_batch_delay:
            t.start_time = time.time()
            a = t.get_complete()
            print('Check complete task {}: {}'.format(t.task['task'], a))
            if a[1] is None:
                if a[0] == 100:
                    put_task({'task': t.task['task'],
                              'data': [], 'is_done': a[0], "proxy_health": a[2]})
                    del main_tasks[i]
                    del t
                continue
            else:
                if a[0]==0:
                    a[0]=1
                    req = put_task({'task': t.task['task'], 'data': a[1], 'is_done': a[0], 'proxy_health': a[2]})
                if a[0] == 100 or req==2:
                    del main_tasks[i]
                    del t


def mainloop():
    print("OKAY, BEGIN CHEKING")
    while True:
        main()
        time.sleep(2)


if __name__ == '__main__':
    mainloop()
