from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point as GPoint
from django.shortcuts import render, redirect
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from geopy.distance import distance as geopy_distance

from .forms import *
from .models import Kill, Player, Package, Point
from .values import *


def index(request, submit_kill_form=None, submit_package_form=None, submit_point_form=None):
    if request.user.is_authenticated:
        if submit_kill_form is None:
            submit_kill_form = SubmitKill(user=request.user)
        if submit_package_form is None:
            submit_package_form = SubmitPackage(user=request.user)
        if submit_point_form is None:
            submit_point_form = SubmitPoint(user=request.user)

        player = request.user.player

        player_lives = request.user.player.lives
        packages = player.packages.exclude(picked_up=player). \
            filter(opening_time__lt=datetime.now()).order_by('opening_time').reverse()
        points = player.points.exclude(picked_up__user_id__in=[request.user.id]). \
            filter(opening_time__lt=datetime.now()).order_by('opening_time').reverse().values()
        info_messages = player.messages.filter(time__lt=datetime.now()).order_by('time').reverse().all()

    return render(request=request, template_name='hg_app/index.html', context=locals())


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registrace proběhla úspěšně.")
            return redirect("hg_app:index")

        messages.error(request, "Registrace selhala.")
    else:
        form = NewUserForm()
    return render(request=request, template_name="hg_app/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Přihlásil(a) ses jako {username}.")
                return redirect("hg_app:index")
            else:
                messages.error(request, "Nesprávné přihlašovací jméno nebo heslo.")
        else:
            messages.error(request, "Nesprávné přihlašovací jméno nebo heslo.")
    else:
        form = LoginForm()

    return render(request=request, template_name="hg_app/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Odhlášení proběhlo úspěšně")
    return redirect("hg_app:index")


def submit_kill(request):
    assert request.method == "POST"

    submit_kill_form = SubmitKill(request.POST, user=request.user)
    if submit_kill_form.is_valid():
        Kill.objects.create(
            victim=submit_kill_form.cleaned_data['victim'],
            murderer=request.user.player,
            stealth_kill=submit_kill_form.cleaned_data['stealth_kill'],
            time=datetime.now()
        )
        messages.info(request, f"Kill zadán.")
    return index(request, submit_kill_form=submit_kill_form)

@login_required
def submit_package(request):
    if not request.method == "POST":
        return redirect('/')

    submit_package_form = SubmitPackage(request.POST, user=request.user)

    if submit_package_form.is_valid():
        package = submit_package_form.cleaned_data['package']
        package.picked_up = request.user.player
        package.save()

        messages.info(request, f"Balíček zadán.")
        return redirect('/')

    return index(request, submit_package_form=submit_package_form)

@login_required
def submit_point(request):
    if not request.method == "POST":
        return redirect('/')

    submit_point_form = SubmitPoint(request.POST, user=request.user)

    if submit_point_form.is_valid():
        point = submit_point_form.cleaned_data['point_id']
        lat = submit_point_form.cleaned_data['latitude']
        long = submit_point_form.cleaned_data['longitude']

        player_point = GPoint(long, lat, srid=4326)
        distance_in_m = point.location.distance(player_point)*100000


        if point.picked_up.count() == point.max_number_of_visits:
            messages.error(request,
                           f"Point nemohl být ověřen. Už byl před tebou navštíven {point.max_number_of_visits}/{point.max_number_of_visits} lidí")
        else:
            if distance_in_m <= MAX_DISTANCE_FROM_POINT:
                point.picked_up.add(request.user.player)
                point.save()
                messages.info(request,
                              f"Point úspěšně ověřen. Je teď navštíven {point.picked_up.count()}/{point.max_number_of_visits} lidí")
            else:
                messages.error(request,
                               f"Nenacházíš se dostatečně blízko. Ověř si, že jsi na správném místě.")

        return redirect('/')
    return index(request, submit_point_form=submit_point_form)


def rules(request):
    return render(request=request, template_name="hg_app/rules.html")


def stats(request):
    kills = request.user.player.my_kills.all()
    kills_count = len(kills)
    packages = Package.objects.filter(picked_up=request.user.player)
    packages_count = len(packages)
    points = Point.objects.filter(picked_up__user_id__in=[request.user.id]).all()
    points_count = len(points)
    deaths = request.user.player.my_deaths.all()
    deaths_count = len(deaths)
    return render(request=request, template_name="hg_app/stats.html", context=locals())


def players(request):
    players = Player.objects.exclude(user=request.user).exclude(lives=0).all()
    players_count = len(players)
    dead_players = Player.objects.filter(lives=0).all()
    dead_players_count = len(dead_players)
    return render(request=request, template_name="hg_app/players.html", context=locals())
