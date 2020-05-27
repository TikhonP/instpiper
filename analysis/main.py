from analysis import HitlerClassifier
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


class task:
    def __init__(self, task):
        self.task = task
        self.start_time = time.time()

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
        self.hc = HitlerClassifier(self.fileproxy, self.filedata, process, {
                                   'is_parsed': False, 'is_id': self.task['is_id'], 'from_id': 0})
        self.hc.start()

    def get_complete(self):
        complete = self.hc.how_much_done()
        data = self.hc.get_all_ready_accs()
        complete = int((complete/self.task_len)*100)
        if self.hc.done:
            complete = 100
        return (complete, data)

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
    """task -> {"task": taskid, "data": data, "is_done": 0-100}"""
    data = json.dumps(task)
    print(data)
    tasks = requests.put(url, params=params, data=data)
    tasks = tasks.json()
    if not tasks['status']:
        print('ERROR with request {}'.format(tasks['error']))
        return 1
    return None


def post_task(task):
    """task -> {"task": taskid, "data": data}"""
    tasks = requests.post(url, params=params, data=task).json()
    if not tasks['status']:
        print('ERROR with request {}'.format(tasks['error']))
        return 1
    return None


def newtasks():
    tasks = get_tasks()
    if tasks is None:

        return None
    for t in tasks:
        if t['task'] in main_tasks_ids:
            continue
        print('New task! ', t)
        main_tasks.append(task(t))
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
                              'data': '[]', 'is_done': a[0]})
                    del main_tasks[i]
                    del t
                continue
            elif a[0] > 0:
                put_task({'task': t.task['task'], 'data': str(
                    a[1]).replace("'", '"'), 'is_done': a[0]})
                if a[0] == 100:
                    del main_tasks[i]
                    del t


def mainloop():
    while True:
        main()
        time.sleep(2)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage : python3 main.py <threads count>')
        sys.exit()
    process = int(sys.argv[1])
    mainloop()
