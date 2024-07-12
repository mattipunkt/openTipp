from django.db import models
from django.conf import settings

# Create your models here.
class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, default="Kein Teamname")
    points = models.IntegerField(default=0)
    icon_url = models.CharField(max_length=50)


class Game(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team1")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team2")
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    time = models.DateTimeField(default=None, null=True)
    match_is_finished = models.BooleanField(default=False)
    type = models.CharField(max_length=60)


class Vote(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)


class Points(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    points = models.IntegerField(default=0)
