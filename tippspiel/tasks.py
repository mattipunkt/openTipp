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
from django.contrib.auth.models import User, Group


@periodic_task(crontab(minute='*/1'))
def change_game():
    with open("/tmp/tipptime", "w") as file:
        file.write(str(datetime.now()))
    update_database()


def update_current_tab():
    currtime = timezone.now()
    currgroup = None
    for game in models.Game.objects.all():
        if game.time > currtime:
            currgroup = game.type.id
        break
    with open("/tmp/currtab", "w") as file:
        file.write(str(currgroup))


def evaluate_points():
    for vote in models.Vote.objects.all():
        if vote.game.match_is_finished:
            points = 0
            game = vote.game
            if game.team1_score == game.team2_score:
                data_winner = "Tie"
            elif game.team1_score > game.team2_score:
                data_winner = "Team1"
            elif game.team1_score < game.team2_score:
                data_winner = "Team2"
            if vote.team1_score == vote.team2_score:
                voter_winner = "Tie"
            elif vote.team1_score > game.team2_score:
                voter_winner = "Team1"
            elif game.team1_score < vote.team2_score:
                voter_winner = "Team2"

            if voter_winner == data_winner:
                points = 1
                # RICHTIG GETIPPT
                if vote.team1_score == game.team1_score:
                    if vote.team2_score == game.team2_score:
                        points = 5
                # RICHTIGE DIFFERENZ GETIPPT
                data_differenz = game.team1_score - game.team2_score
                voter_differenz = vote.team1_score - vote.team2_score
                if data_differenz == voter_differenz:
                    points = 3
            else:
                points = 0
        else:
            points = 0
        vote.points = points
        vote.save()


def evaluate_scores():
    evaluate_points()
    for user in User.objects.all():
        score = 0
        for vote in models.Vote.objects.all().filter(user=user):
            score += vote.points
        user_points = models.Points.objects.get_or_create(user=user)
        user_points[0].points = score
        user_points[0].save()


def update_database():
    # url = get_json("https://api.openligadb.de/getmatchdata/em/2024/")
    url = get_json("https://api.openligadb.de/getmatchdata/bl2")
    for game in url:
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
        if matchtime < datetime.now():
            is_started = True
        else:
            is_started = False
        if game['matchIsFinished']:
            is_started = False
            # print('Match is finished')
            points_team1 = 0
            points_team2 = 0
            for k in game['matchResults']:
                points_team1 = k['pointsTeam1']
                points_team2 = k['pointsTeam2']
            update_game = models.Game.objects.get_or_create(team1=team1[0], team2=team2[0], time=matchtime, match_is_started=is_started,
                                                            type=type_of_game[0])
            update_game[0].team1_score = points_team1
            update_game[0].team2_score = points_team2
            update_game[0].match_is_finished = True
            update_game[0].save()
        else:
            new_game = models.Game.objects.get_or_create(team1=team1[0], team2=team2[0], time=matchtime, match_is_started=is_started,
                                                         type=type_of_game[0])
            new_game[0].save()

    update_current_tab()
    evaluate_scores()


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
