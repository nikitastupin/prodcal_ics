# Как использовать?
Ссылка на подписной календарь: http://towerinfog.ml/prodcal.ics

### Настройка подписного календаря на iOS
![Шаг 1](http://towerinfog.ml/guides/iphone-guide.jpg)
### Настройка подписного календаря на MacOS
...
### Настройка подписного календаря в Google Calendar
...

# Как поднять у себя на сервере
1. Установить необходимые модули для Python:
    1. more_itertools
    1. icalendar
1. Настроить автообновление календаря:
```
$ crontab -l
0 1 * * * python /home/ubuntu/prodcal_ics.py --start-year=2018 -o /home/ubuntu/www/prodcal.ics
```
1. Отдавать файл любым сервером prodcal.ics (например, nginx)
