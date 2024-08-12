from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from . import forms
from django.contrib import messages
import asyncio
from . import tasks
from . import models
from . import utils
import json
import configparser

from .models import Points

# Create your views here.
task_id = None


def index(request):
    return render(request, 'base.html', {
        "games": models.Game.objects.all(),
    })


def setup(request):
    if utils.config_exists() == True:
            return redirect('/')
    if request.method == "POST":
        form = forms.SetupForm(request.POST)
        if form.is_valid():
            print("=== Create Super User ===")
            su = User.objects.create_superuser(request.POST.get('admin_username'), request.POST.get('admin_email'), request.POST.get('admin_password'))
            su.first_name = request.POST.get('admin_first_name')
            su.save()
            print("=== Create init config ===")
            utils.set_config('refresh_interval', request.POST.get('intervall'))
            utils.set_config('setup_done', True)

            return redirect('/')
        else: 
            return redirect('/setup/')
    else:
        print(utils.config_exists())
        if utils.config_exists() == False:
            return render(request, 'setup.html', {
                "setupForm": forms.SetupForm,
            })
        elif utils.config_exists() == True:
            return redirect('/')


def register(request):
    registerform = forms.RegisterForm()
    if request.method == 'POST':
        registerform = forms.RegisterForm(request.POST)
        if registerform.is_valid():
            username = request.POST['username']
            first_name = request.POST['first_name']
            email = request.POST['email']
            password = request.POST['password']
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                            is_active=False)
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Deine Registrierung war erfolgreich. Der Admin muss jetzt '
                                                            'deinen Account bestätigen. Wenn dies geschehen ist, erhälst du '
                                                            'eine E-Mail. Dann kannst du fleißig lostippen.')
        else:
            messages.add_message(request, messages.ERROR, 'Die Eingabe war nicht erfolgreich! Bitte die Registrierung '
                                                          'erneut versuchen!')
        return redirect("/")
    else:
        return render(request, 'register.html', {
            "registerForm": registerform,
        })


def loginPage(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Du wurdest erfolgreich angemeldet!")
            return redirect('/')
        else:
            messages.add_message(request, messages.ERROR,
                                 "Entweder ist dein Benutzername oder Passwort falsch oder dein Account wurde noch nicht freigeschaltet. Hast du schon eine Mail bekommen? Bitte erneut versuchen.")
            return redirect('/')
    else:
        return render(request, 'login.html', {
            "loginForm": forms.LoginForm,
        })


def logoutUser(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Du wurdest erfolgreich ausgeloggt. Bis bald!")
    return redirect('/')


def adminBackend(request):
    if request.user.is_superuser:
        in_users = User.objects.all().filter(is_active=False)
        active_users = User.objects.all().filter(is_active=True)
        return render(request, 'admin.html', {
            'in_users': in_users,
            'active_users': active_users,
            'daemon_running': tasks.is_task_scheduled(),
            'last_time_running': tasks.last_time_running(),
        })
    return render(request, 'admin.html')


def userManager(request):
    if request.user.is_superuser:
        if request.method == "GET":
            action = request.GET.get('action')
            if action == "activate":
                user_id = request.GET.get('id')
                activate = request.GET.get('activate')
                user = User.objects.get(pk=user_id)
                if activate == "true":
                    user.is_active = True
                    utils.send_activation_mail(user)
                    user.save()
                elif activate == "false":
                    user.delete()
            if action == "superuser":
                user_id = request.GET.get('id')
                activate = request.GET.get('activate')
                user = User.objects.get(pk=user_id)
                if activate == "true":
                    user.is_superuser = True
                    user.save()
        return redirect("/admin")
    else:
        return redirect("/")


def gamesView(request):
    return render(request, 'games.html', {
        "gametype": models.GameType.objects.all(),
        "games": models.Game.objects.all(),
    })


def betSubmussion(request):
    if request.method == 'GET':
            return redirect("/")
    elif request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            if request.method == 'POST':
                data = json.load(request)
                test = dict(data)
                # print(test)
                for vote in test:
                    # print(vote)
                    if models.Game.objects.get(pk=vote).match_is_finished:
                        # print("Game is finished")
                        messages.add_message(request, messages.WARNING,
                                             "Du sollst nicht für ein Spiel tippen, das schon beendet wurde, du Schlawiner!")
                        return JsonResponse({'status': 'Match finished!'})
                    else:
                        game_id = vote
                        vote = test[vote]
                        if vote['team1_vote'] == "":
                            team_1_vote = None
                        else:
                            team_1_vote = vote['team1_vote']

                        if vote['team2_vote'] == "":
                            team_2_vote = None
                        else:
                            team_2_vote = vote['team2_vote']
                        vote_obj = models.Vote.objects.get_or_create(user=request.user,
                                                                     game=models.Game.objects.get(pk=game_id))
                        # print(vote_obj[1])
                        vote_obj = vote_obj[0]
                        vote_obj.team1_score = team_1_vote
                        vote_obj.team2_score = team_2_vote
                        vote_obj.save()
                return JsonResponse({'status': 'Votes registered!'})
        else:
            return HttpResponseBadRequest('Invalid request')


def betView(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_votes = models.Vote.objects.select_related('game').filter(user=request.user)
            user_votes_dict = {vote.game.id: vote for vote in user_votes}
            return render(request, 'bet.html', {
                # "activegroup": utils.get_current_tab(),
                "user_votes_dict": user_votes_dict,
                "gametype": models.GameType.objects.all(),
                "games": models.Game.objects.all(),
            })
        else:
            messages.add_message(request, messages.INFO, "Du musst angemeldet sein, um diese Seite zu besuchen!")
            return redirect("/")


def statisticsView(request):
    if request.user.is_authenticated:
        return render(request, 'statistics.html', {
            "points": models.Points.objects.all().order_by('-points'),
        })


def statisticsUserView(request, id):
    user = User.objects.get(pk=id)
    votes = models.Vote.objects.select_related('game').filter(user=user)
    finished = votes.filter(game__match_is_finished=True)
    return render(request,'userStats.html', {
        "points": Points.objects.get(user=user),
        "votes": finished,
    })