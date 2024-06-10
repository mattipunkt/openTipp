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
