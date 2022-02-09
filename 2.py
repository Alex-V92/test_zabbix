import argparse
import sqlite3
import csv

# Создание аргументов для командной строки
parser = argparse.ArgumentParser(description='Экспорт выбранного типа данных из zabbix в csv/db')
parser.add_argument('--sql', metavar='имя базны данных', help='Запись в SQLite3 элементов данных')
parser.add_argument('--csv', metavar='имя csv файла', help='Запись в CSV элементов данных')
parser.add_argument('-hostgroup', metavar='группа поиска', nargs='+', help='Выбор группы хостов')
parser.add_argument('-metric', metavar='название элемента данных', nargs='+', help='Выбор элемента данных')
args = parser.parse_args()

# Создание переменных на основе переданных аргументов и проверка на указанный тип данных
sql_name = args.sql
csv_name = args.csv

if sql_name == None and csv_name == None:
    raise ('Не указан тип записи. Наберите -h или --help для справки')

metric = ' '.join(args.metric)
hostgroup = ' '.join(args.hostgroup)

if metric == None or hostgroup == None:
    raise Exception('Неверный формат группы хостов или типа метрики. Нажмите -h для справки')

# ТЕСТ ПЕРЕДАННЫХ ДАННЫХ ОТ ЗАББИКС СЕРВЕРА.УДАЛИТЬ
tuple_zabbix = (
    ['333', '3333', 'asdasdasdasd', ],
    ['444', '4444777 1', '44444', ],
    ['555', 'asdasdas', '666 6', ],
)

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
        connection.executemany(sqlite_insert, tuple_zabbix)
        connection.commit()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQL', error)

# Создание БД, если передан необязательный аргумент sql
if csv_name != None:
    print('Запись в csv')
    with open(f'{csv_name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Hostname', 'Lasclock', 'Description'])
        writer.writerows(tuple_zabbix)

print('Завершено')
