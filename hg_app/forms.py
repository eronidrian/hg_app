from datetime import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Player, Point


class NewUserForm(UserCreationForm):
    username = forms.CharField(label='Přihlašovací jméno', min_length=5, max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    password1 = forms.CharField(label='Heslo', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Heslo znovu pro potvrzení', widget=forms.PasswordInput, required=True)

    def username_clean(self):
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username=username)
        if new.count():
            raise ValidationError("Hráč se zadaným jmnénem už existuje")
        return username

    def email_clean(self):
        email = self.cleaned_data['email'].lower()
        new = User.objects.filter(email=email)
        if new.count():
            raise ValidationError(" Email je už použitý")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Hesla se neshodují")
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(label='Heslo', widget=forms.PasswordInput, required=True)


class SubmitKill(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SubmitKill, self).__init__(*args, **kwargs)
        self.fields['victim'].queryset = Player.objects.exclude(user=self.user).exclude(lives=0)

    victim = forms.ModelChoiceField(Player.objects.none(), label='Oběť', empty_label="Vyber, koho jsi zabil(a)")
    stealth_kill = forms.BooleanField(label='Stealth kill', required=False)


class SubmitPoint(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(SubmitPoint, self).__init__(*args, **kwargs)

        self.fields['point_id'].queryset = user.player.points.exclude(picked_up__user=user). \
            filter(opening_time__lt=datetime.now())

    point_id = forms.ModelChoiceField(queryset=Point.objects.none(), label="ID pointu",
                                      empty_label="Vyber, jaký point jsi našel/našla", required=True,
                                      widget=forms.Select(attrs={'id': 'id_point'}))

    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Balíček #{obj.id}"


class SubmitPackage(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SubmitPackage, self).__init__(*args, **kwargs)
        self.fields['package'].queryset = self.user.player.packages.exclude(picked_up=self.user.player). \
            filter(opening_time__lt=datetime.now()).all()

    package = MyModelChoiceField(queryset=Player.objects.none(), label="ID balíčku",
                                 empty_label="Vyber, jaký balíček jsi našel/našla", required=False)
