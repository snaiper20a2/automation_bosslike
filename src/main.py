import time

import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC


data = open('data/login_data.txt', 'r')
key = data.readline()


# response = requests.get('https://api-public.bosslike.ru/v1/bots/users/me/', headers={'Accept': 'application/json',
#                                                                                      'X-Api-Key': key})
# tasks = requests.get('https://api-public.bosslike.ru/v1/bots/tasks/?service_type=3&task_type=3',
#                      headers={'Accept': 'application/json',
#                               'X-Api-Key': key})
# tasks = json.loads(str(tasks.text))
# for item in tasks['data']['items']:
#     print(item)


class SubscribeManager:
    def __init__(self):
        self.driver = webdriver.Chrome('webDriver/chromedriver')
        self.login_data = open('data/instagram_data.txt', 'r')
        self.login_instagram = self.login_data.readline()
        self.password_instagram = self.login_data.readline()
        self.driver.get('https://www.instagram.com/accounts/login/?next=%2Fstone_by_stonehedge%2F&source=desktop_nav')
        wait = WebDriverWait(self.driver, 10, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        login_label = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[aria-label='Номер телефона, имя пользователя или эл. адрес']")))
        login_label.send_keys(self.login_instagram)
        password_label = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Пароль']")))
        password_label.send_keys(self.password_instagram)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        time.sleep(1)
        button.click()
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Сохранить данные']")))
        time.sleep(1)
        button.click()

    def do(self, task):
        self.driver.get(task['data']['url'])
        time.sleep(20)
        wait = WebDriverWait(self.driver, 5, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        try:
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Подписаться']")))
            button.click()
            return True
        finally:
            return True


# sub = SubscribeManager()


# tasks = requests.get('https://api-public.bosslike.ru/v1/bots/tasks/?service_type=3&task_type=3',
#                      headers={'Accept': 'application/json',
#                               'X-Api-Key': key})
# tasks = json.loads(str(tasks.text))
# print(tasks['data'])
# sub.do(tasks)

class Task:
    id = None
    name = None
    price = None

    def __str__(self):
        return str(self.id) + ' ' + str(self.name) + ' ' + str(self.price)


class TaskManager:
    tasks = None
    last_task_id = 0

    def __init__(self):
        self.sub = SubscribeManager()

    def upateTasks(self):  # Данный метод обновляет список заданий, разбирая ответ в объект self.tasks
        tasks = requests.get('https://api-public.bosslike.ru/v1/bots/tasks/?service_type=3&task_type=3',
                             headers={'Accept': 'application/json',
                                      'X-Api-Key': key})
        tasks = json.loads(str(tasks.text))
        data = tasks['data']
        self.tasks = []
        for item in data['items']:
            task = Task()
            task.id = item['id']
            task.name = item['name']['object']
            task.price = item['price']['value']
            self.tasks.append(task)

    def start(self):  # Данный метод берет на выполнение задания, проверяет их
        self.upateTasks()
        counter = 0
        for task in self.tasks:
            if counter > 150:
                break
            print(counter)
            self.upateTasks()
            task_data = requests.get('https://api-public.bosslike.ru/v1/bots/tasks/' + task.id + '/do/',
                                     headers={'Accept': 'application/json',
                                              'X-Api-Key': key})
            task_data = json.loads(str(task_data.text))
            if task_data['status'] < 400:
                print(task_data)
                if self.sub.do(task_data):
                    task_data = requests.get('https://api-public.bosslike.ru/v1/bots/tasks/' + task.id + '/check/',
                                             headers={'Accept': 'application/json',
                                                      'X-Api-Key': key})
                    task_data = json.loads(str(task_data.text))
                    print('статус:', task_data['success'])
                    if task_data['success']:
                        counter += 1
                        self.last_task_id = task.id
                        print('баллы:', task_data['data'])
                        task_data = requests.post(
                            'https://api-public.bosslike.ru/v1/bots/tasks/' + task.id + '/hide/',
                            headers={'Accept': 'application/json',
                                     'X-Api-Key': key})
                        task_data = json.loads(str(task_data.text))
                        print(task_data)  # 'скрыто:', task_data['success'], task_data['status'])
                        time.sleep(1)
                        self.last_task_id = task.id
                    else:
                        if self.last_task_id == task.id:
                            task_data = requests.post(
                                'https://api-public.bosslike.ru/v1/bots/tasks/' + task.id + '/hide/',
                                headers={'Accept': 'application/json',
                                         'X-Api-Key': key})
                            task_data = json.loads(str(task_data.text))
                            print(task_data)
                            time.sleep(1)
                            self.last_task_id = task.id


manager = TaskManager()
manager.start()
