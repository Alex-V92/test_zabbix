from pyzabbix import ZabbixAPI
from datetime import datetime, timedelta
import sys

# дельта для корректного отображения времени с учётом часового пояса
delta = timedelta(hours=3, minutes=0)

# подключение к тестовому стенду
zapi = ZabbixAPI('http://172.16.2.2/zabbix', user='Admin', password='zabbix')

# получение списка всех групп и итерация по всем найденным элементам, пока не найдёт нужный нам
groups = zapi.hostgroup.get(output=['itemid', 'name'])
for group in groups:
    if group['name'] == 'Discovered hosts':
        idgroup = group['groupid']
        namegroup = group['name']
        break
# наименование столбцов таблицы
print(f'Hostname{" " * 8} | lastdate{" " * 12}| Memory utilization')

# список всех найденных хостов по id, который нашли в предыдущем цикле
hosts = zapi.host.get(groupids=idgroup, output=['hostid', 'name'])

# список всех хостов idgroup и соответствующий им элемент данных по утилизации
# оперативной памяти, а так же итерация и вывод в табличном формате
items = zapi.item.get(groupids=idgroup, filter={'name': 'Memory utilization'})
for item in items:
    for i in (tuple(filter(lambda x: x['hostid'] == item['hostid'], hosts))):
        print(i['name'].ljust(16), end=' | ')
    print(datetime.utcfromtimestamp(int(item['lastclock'])) + delta, '|', item['lastvalue'][:5] + '%')
