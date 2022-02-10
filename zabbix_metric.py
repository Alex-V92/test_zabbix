#!/usr/bin/python3
from pyzabbix import ZabbixAPI
from datetime import datetime
import os
import argparse
import sqlite3
import csv

# Создание аргументов для командной строки
parser = argparse.ArgumentParser(description='Экспорт выбранного типа данных из zabbix в csv/db')
parser.add_argument('--sql', metavar='имя базны данных', help='Запись в SQLite3 элементов данных')
parser.add_argument('--csv', metavar='имя csv файла', help='Запись в CSV элементов данных')
parser.add_argument('-g', metavar='группа поиска', help='Выбор группы хостов')
parser.add_argument('-m', metavar='название элемента данных', help='Выбор элемента данных')
parser.add_argument('-z', metavar='zabbix сервер', help='адрес zabbix сервера')
args = parser.parse_args()

# Создание переменных на основе переданных аргументов и проверка на указанный тип данных
sql_name = args.sql
csv_name = args.csv

if sql_name == None and csv_name == None:
    raise ('Не указан тип записи. Наберите -h или --help для справки')

metric = args.m
hostgroup = args.g
zabbix_server = args.z

if metric == None or hostgroup == None:
    raise Exception('Неверный формат группы хостов или типа метрики. Нажмите -h для справки')

# подключение к тестовому стенду
zapi = ZabbixAPI(zabbix_server, user=os.environ.get('ZABBIX_USERNAME'), password=os.environ.get('ZABBIX_PASSWORD'))
if os.environ.get('ZABBIX_USERNAME') == None or os.environ.get('ZABBIX_PASSWORD') == None:
    raise ('Не указаны переменные окружения ZABBIX_USERNAME и ZABBIX_PASSWORD')

# получение списка всех групп и итерация по всем найденным элементам, пока не найдёт нужный нам
groups = zapi.hostgroup.get(output=['itemid', 'name'])
for group in groups:
    if group['name'] == hostgroup:
        idgroup = group['groupid']
        namegroup = group['name']
        break

# список всех найденных хостов по id, который нашли в предыдущем цикле
try:
    hosts = zapi.host.get(groupids=idgroup, output=['hostid', 'name'])
except NameError:
    raise ('Неверно указана группа хостов')

# список всех хостов idgroup и соответствующий им элемент данных
items = zapi.item.get(groupids=idgroup, filter={'name': metric})
if len(items) == 0:
    raise ('Неверно указан элемент данных')
metric_list = []
for item in items:
    list_host_metric = []
    list_host_metric.append(list(filter(lambda x: x['hostid'] == item['hostid'], hosts))[0]['name'])
    list_host_metric.append(datetime.fromtimestamp(int(item['lastclock'])).strftime('%Y-%m-%d %H:%M:%S'))
    list_host_metric.append(item['lastvalue'][:5])
    metric_list.append(list_host_metric)

# Создание БД, если передан необязательный аргумент sql
if sql_name != None:
    print('Запись в SQLite')
    try:
        connection = sqlite3.connect(f'{sql_name}.db')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Metrica
        (Hostname TEXT, Lastclock TEXT, Lastvalue TEXT)''')
        connection.execute('DELETE FROM Metrica')
        sqlite_insert = 'INSERT INTO Metrica VALUES (?, ?, ?)'
        connection.executemany(sqlite_insert, metric_list)
        connection.commit()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQL', error)

# Создание БД, если передан необязательный аргумент sql
if csv_name != None:
    print('Запись в csv')
    with open(f'{csv_name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Hostname', 'Lasclock', 'Description'])
        writer.writerows(metric_list)

print('Завершено')
