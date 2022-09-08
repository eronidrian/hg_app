from datetime import datetime, timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q, F, Count
from django.core.exceptions import ValidationError

from .models import Player, Point, Package, AdminConfiguration


class NewUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        if commit:
            user.save()
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
        hide_after = AdminConfiguration.objects.get(id=1).hide_after

        self.fields['point_id'].queryset = user.player.points.exclude(picked_up__user=user). \
            filter(opening_time__lt=datetime.now()).annotate(num=Count('picked_up')).\
            exclude(Q(opening_time__lt=datetime.now() - timedelta(hours=hide_after))
                    & Q(num__gte=F('max_number_of_visits')))

    point_id = forms.ModelChoiceField(queryset=Point.objects.none(), label="ID pointu",
                                      empty_label="Vyber, jaký point jsi našel/našla", required=True,
                                      widget=forms.Select(attrs={'id': 'id_point'}))

    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())


class SubmitPackage(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SubmitPackage, self).__init__(*args, **kwargs)
        hide_after = AdminConfiguration.objects.get(id=1).hide_after
        self.fields['package_id'].queryset = self.user.player.packages.exclude(picked_up=self.user.player). \
            filter(opening_time__lt=datetime.now()).exclude(Q(opening_time__lt=datetime.now() - timedelta(hours=hide_after))
                                                            & Q(picked_up__isnull=False))

    package_id = forms.ModelChoiceField(queryset=Package.objects.none(), label="ID balíčku",
                                      empty_label="Vyber, jaký balíček jsi našel/našla", required=True,
                                      widget=forms.Select(attrs={'id': 'id_package'}))

class SubmitSpecial(forms.Form):
    verification_code = forms.CharField(label="Ověřovací kód", required=True)


class ProfilePicture(forms.Form):
    photo = forms.ImageField(label="", required=True)