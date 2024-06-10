import huey
from huey import crontab
from huey import crontab
from huey.contrib.djhuey import periodic_task, task, db_task, HUEY
from huey.api import Result
import os
import time
from datetime import datetime, timedelta


@periodic_task(crontab(minute=5))
def change_game():
    with open("/tmp/tipptime", "w") as file:
        file.write(str(datetime.now()))


def is_task_scheduled():
    file = open("/tmp/tipptime", "r")
    line = file.read()
    file.close()
    last_time = datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f")
    if datetime.now() - last_time > timedelta(minutes=6):
        return False
    else:
        return True


def last_time_running():
    file = open("/tmp/tipptime", "r")
    line = file.read()
    file.close()
    return datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f")
