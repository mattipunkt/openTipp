from django.core.mail import send_mail
from huey import crontab
from huey.contrib.djhuey import periodic_task, task, db_task, HUEY
from huey.api import Result
import os
import time
from datetime import datetime, timedelta
import requests
import json
from . import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.conf import settings
import configparser
from appdirs import *

appname = "opentipp"

def get_current_tab():
    with open("/tmp/currtab", "r") as file:
        return int(file.read())


@task()
def send_activation_mail(user):
    send_mail(
        subject="[TIPPSPIEL] Dein Account wurde aktiviert!",
        message="Hallo " + user.first_name + ",\n\nDer Administrator hat deinen Account aktiviert und du kannst anfangen zu tippen!\n\nViele Grüße,\nDein Tippspiel-Team\n\nViel Spaß beim Tippen!",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )


def config_exists():
    if os.path.exists(user_config_dir(appname) + '/opentipp_settings.ini'):
        return True
    else:
        return False


def get_config(key):
    parser = configparser.ConfigParser()
    parser.read(user_config_dir(appname) + '/opentipp_settings.ini')
    return parser.get('SETTINGS', str(key))


def set_config(key, value):
    config = configparser.ConfigParser()
    print(config_exists())
    if config_exists() == False:
        if not os.path.exists(user_config_dir(appname)):
            os.mkdir(user_config_dir(appname))
        with open(user_config_dir(appname) + '/opentipp_settings.ini', 'w+') as file:
            file.write("[SETTINGS]")
    if config_exists() == True:
        config.read(user_config_dir(appname) + '/opentipp_settings.ini')
    config['SETTINGS'][str(key)] = str(value)
    with open(user_config_dir(appname) + '/opentipp_settings.ini', 'w') as configfile:
        config.write(configfile)
