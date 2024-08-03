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
