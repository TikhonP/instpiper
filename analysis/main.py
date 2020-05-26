from analysis import HitlerClassifier
import json
import os
import requests
import time


dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, '../config.json'), 'r') as f:
    config = json.load(f)
    tokens = config['private_tokens']
    domen = config['domen']

params = {'token': tokens[0]}
url = domen+'/api/private'

main_tasks = []
main_tasks_ids = []

get_batch_delay = 30

proxypath = 'openproxy.txt'

process = 1


class task:
    def __init__(self, task):
        self.task = task
        self.start_time = time.time()

    def begin(self):
        self.filedata = os.path.join(
            dir_path, 'task_files/{}.txt'.format(self.task['task']))
        with open(self.filedata, 'w') as f:
            f.write(self.task['data'])
        self.hc = HitlerClassifier(proxypath, self.filedata, process, {
                                   'is_parsed': False, 'is_id': False, 'from_id': 0})
        self.hc.start()

    def get_complete(self):
        print('checking complete in class')
        complete = self.hc.how_much_done()
        print('is done - ', complete)
        data = self.hc.get_all_ready_accs()
        print('data - ', data)
        if self.hc.is_done():
            complete = 100
        return (complete, data)

    def __del__(self):
        os.remove(self.filedata)
        del self.hc


def get_tasks():
    tasks = requests.get(url, params=params).json()
    if not tasks['status']:
        print('ERROR with request {}'.format(tasks['error']))
        return None
    if tasks['data'] == 0:
        return None
    return tasks['data']


def patch_task(task):
    """task -> {"task": taskid, "data": data, "is_done": 0-100}"""
    tasks = requests.patch(url, params=params, data=task).json()
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
        print(time.time()-t.start_time, get_batch_delay)
        if (int(time.time()-t.start_time))>= get_batch_delay:
            print('Checking complete...')
            t.start_time = time.time()
            a = t.get_complete()
            print('Check complete: ', a)
            if a[0] == 100:
                patch_task({'task': t.task['task'], 'data': a[1], 'is_done': a[0]})
                del main_tasks[i]
            if a[0] > 0:
                patch_task({'task': t.task['task'], 'data': a[1], 'is_done': a[0]})
    '''
    if len(list_to_destroy) != 0:
        for i in list_to_destroy:
            main_tasks.pop(i)
            main_tasks_ids.pop(i)
'''

def mainloop():
    while True:
        main()
        time.sleep(2)


if __name__ == '__main__':
    mainloop()
