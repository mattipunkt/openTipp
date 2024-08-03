from django.urls import path, include

import tippspiel
from . import views

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('admin/', views.adminBackend, name="admin"),
    path('users', views.userManager, name="activate"),
    path('games/', views.gamesView, name="games"),
    path('bet/', views.betView, name="bet"),
    path('stats/', views.statisticsView, name="stats"),
    path('userStats/<int:id>', views.statisticsUserView, name="userStats"),
    path('betPush/', views.betSubmussion, name="betSubmussion"),
]
