from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(label="Benutzername")
    first_name = forms.CharField(label="Vorname")
    email = forms.EmailField(label="E-Mail-Adresse")
    password = forms.CharField(widget=forms.PasswordInput, label="Passwort vergeben")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Passwort wiederholen")


class LoginForm(forms.Form):
    username = forms.CharField(label="Benutzername")
    password = forms.CharField(widget=forms.PasswordInput, label="Passwort")


class SetupForm(forms.Form):
    intervall = forms.IntegerField(label="Aktualisierung der Daten von openLigaDB (in Minuten; weniger als 4min werden nicht empfohlen!)", initial=5)
    admin_username = forms.CharField(label="Benutzername für den Admin")
    admin_first_name = forms.CharField(label="Vorname des Admins")
    admin_email = forms.CharField(label="E-Mail des Admins")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Passwort für den Admin")
