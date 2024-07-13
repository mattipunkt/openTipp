import huey
from huey import crontab
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


@periodic_task(crontab(minute=5), expires=timedelta(seconds=0))
def change_game():
    with open("/tmp/tipptime", "w") as file:
        file.write(str(datetime.now()))
    update_database()


def update_current_tab():
    currtime = timezone.now()
    for game in models.Game.objects.all():
        if game.time > currtime:
            currgroup = game.type.id
        break
    with open("/tmp/currtab", "w") as file:
        file.write(str(currgroup))



def update_database():
    nr = [1, 2, 3, 4, 5, 6, 7]
    for i in nr:
        j = get_json("https://api.openligadb.de/getmatchdata/em/2024/" + str(i))

        for game in j:
            team1_icon_url = game['team1']['teamIconUrl']
            if "px" in team1_icon_url:
                parts = team1_icon_url.split('/')
                for k, part in enumerate(parts):
                    if 'px-' in part:
                        # Ersetze die aktuelle Pixelzahl mit der neuen Pixelzahl
                        parts[k] = f'200px-{parts[k].split("px-")[1]}'
                team1_icon_url = '/'.join(parts)

            team2_icon_url = game['team2']['teamIconUrl']
            if "px" in team2_icon_url:
                parts = team2_icon_url.split('/')
                for k, part in enumerate(parts):
                    if 'px-' in part:
                        # Ersetze die aktuelle Pixelzahl mit der neuen Pixelzahl
                        parts[k] = f'200px-{parts[k].split("px-")[1]}'
                team2_icon_url = '/'.join(parts)

            team1 = models.Team.objects.get_or_create(id=game['team1']['teamId'], name=game['team1']['teamName'],
                                                      icon_url=team1_icon_url)
            team2 = models.Team.objects.get_or_create(id=game['team2']['teamId'], name=game['team2']['teamName'],
                                                      icon_url=team2_icon_url)
            type_of_game = models.GameType.objects.get_or_create(name=game['group']['groupName'])
            matchtime = game['matchDateTime']
            matchtime = datetime.strptime(matchtime, "%Y-%m-%dT%H:%M:%S")
            if game['matchIsFinished']:
                # print('Match is finished')
                points_team1 = 0
                points_team2 = 0
                for k in game['matchResults']:
                    points_team1 = k['pointsTeam1']
                    points_team2 = k['pointsTeam2']
                update_game = models.Game.objects.get_or_create(team1=team1[0], team2=team2[0], time=matchtime, type=type_of_game[0])
                update_game[0].team1_score = points_team1
                update_game[0].team2_score = points_team2
                update_game[0].match_is_finished = True
                update_game[0].save()
            else:
                new_game = models.Game.objects.get_or_create(team1=team1[0], team2=team2[0], time=matchtime, type=type_of_game[0])
                new_game[0].save()

    update_current_tab()


def get_json(url):
    response = requests.get(url).text
    j = json.loads(response)
    return j


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
