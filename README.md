# Как добавить в календарь MacOS или iOS, Google Calendar
http://towerinfog.ml/prodcal.ics

# Как поднять у себя на сервере
Необходимые модули Python:
more_itertools
icalendar

$ crontab -l
0 1 * * * python /home/ubuntu/prodcal_ics.py --start-year=2018 -o /home/ubuntu/www/prodcal.ics
