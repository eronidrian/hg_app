from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.gis.geos import Point as GPoint
from django.http import HttpResponse
from django.db.models import Q, Count, F
from django.core.exceptions import PermissionDenied



from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from django.conf import settings


from .forms import *
from .models import *



def index(request, submit_kill_form=None, submit_package_form=None, submit_point_form=None, submit_special_form=None):
    if request.user.is_authenticated:
        if submit_kill_form is None:
            submit_kill_form = SubmitKill(user=request.user)
        if submit_package_form is None:
            submit_package_form = SubmitPackage(user=request.user)
        if submit_point_form is None:
            submit_point_form = SubmitPoint(user=request.user)
        if submit_special_form is None:
            submit_special_form = SubmitSpecial()
        if request.user.is_superuser:
            return redirect("hg_app:epic_map")
        player = request.user.player

        player_lives = player.lives
        hide_after = AdminConfiguration.objects.get(id=1).hide_after
        packages = player.packages.exclude(picked_up=player). \
            filter(opening_time__lt=datetime.now()).exclude(Q(opening_time__lt=datetime.now() - timedelta(hours=hide_after))
                                                            & Q(picked_up__isnull=False))
        points = player.points.exclude(picked_up__user_id__in=[request.user.id]). \
            filter(opening_time__lt=datetime.now()).annotate(num=Count('picked_up')).\
            exclude(Q(opening_time__lt=datetime.now() - timedelta(hours=hide_after))
                    & Q(num__gte=F('max_number_of_visits')))
        info_messages = Message.objects.filter(time__lt=datetime.now()).filter(players__user_id__in=[request.user.id])
        quest = player.quest
        trophy_count = player.trophy_count
        trophy_multiply = 2**trophy_count
        trophy_players = Player.objects.exclude(user=request.user).exclude(trophy_count=0)
        debug_flag = settings.DEBUG
        if_show_players = AdminConfiguration.objects.get(id=1).show_people
        show_players = Player.objects.exclude(location_history=None)
        turn_off = AdminConfiguration.objects.get(id=1).turn_off
        end_game = AdminConfiguration.objects.get(id=1).end_game

        if not player.photo:
            messages.warning(request, "Nemáš nahranou profilovou fotku. Nahraj si ji prosím v záložce \"Změnit údaje\"")
        if not player.location_history:
            messages.warning(request, "Nemáš povolený přístup k poloze pro tuto stránku. "
                                      "Nezapomeň to aplikaci před hrou povolit")

    return render(request=request, template_name='hg_app/index.html', context=locals())


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registrace proběhla úspěšně.")
            return redirect("hg_app:index")

        messages.error(request, f"Registrace selhala. ({form.errors.as_data()})")
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
                if user.is_superuser:
                    return redirect("hg_app:epic_map")
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

@login_required
def submit_kill(request):
    assert request.method == "POST"

    submit_kill_form = SubmitKill(request.POST, user=request.user)
    if submit_kill_form.is_valid():
        if submit_kill_form.cleaned_data['victim'].lives == 0:
            Logs.objects.create(
                player=request.user.player,
                brief="kill",
                log=f"Hráč se pokusil zabít hráče {submit_kill_form.cleaned_data['victim']}, ten byl už mrtvý",
            )
            messages.error(request, f"Hráč je již mrtvý. Obnov si stránku v prohlížeči, abys viděl(a) aktuální data")
        if submit_kill_form.cleaned_data['victim'].trophy_count > 0:
            Logs.objects.create(
                player=request.user.player,
                brief="kill",
                log=f"Hráč sebral hráči {submit_kill_form.cleaned_data['victim']} trofej",
            )
            messages.info(request, f"Sebral(a) jsi hráči trofej.")
        if submit_kill_form.cleaned_data['victim'] == request.user.player.quest:
            Logs.objects.create(
                player=request.user.player,
                brief="kill",
                log=f"Hráč zabil hráče {submit_kill_form.cleaned_data['victim']}, na kterého měl quest",
            )
            messages.info(request, f"Zabil(a) jsi hráče, na kterého jsi měl quest. Dostáváš nový quest.")
        Logs.objects.create(
            player=request.user.player,
            brief="kill",
            log=f"Hráč zabil hráče {submit_kill_form.cleaned_data['victim']}",
        )
        Kill.objects.create(
            victim=submit_kill_form.cleaned_data['victim'],
            murderer=request.user.player,
            stealth_kill=submit_kill_form.cleaned_data['stealth_kill'],
            time=datetime.now()
        )
        messages.info(request, f"Kill zadán.")

        return redirect('/')
    return index(request, submit_kill_form=submit_kill_form)

@login_required
def submit_package(request):
    if not request.method == "POST":
        return redirect('/')

    submit_package_form = SubmitPackage(request.POST, user=request.user)

    if submit_package_form.is_valid():
        package = submit_package_form.cleaned_data['package_id']
        if package.picked_up:
            Logs.objects.create(
                player=request.user.player,
                brief="balíček",
                log=f"Hráč se pokusil sebrat balíček {submit_package_form.cleaned_data['package_id']}, ten už byl vybraný",
            )
            messages.error(request, f"Balíček už byl zadán jiným hráčem.")
            return redirect('/')
        Logs.objects.create(
            player=request.user.player,
            brief="balíček",
            log=f"Hráč sebral balíček {submit_package_form.cleaned_data['package_id']}",
        )
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
        conf = AdminConfiguration.objects.get(id=1)
        if distance_in_m > conf.max_distance_from_point:
            Logs.objects.create(
                player=request.user.player,
                brief="point",
                log=f"Hráč se pokusil sebrat point {submit_point_form.cleaned_data['point_id']}, ale nebyl dost blízko",
            )
            messages.error(request,
                           f"Nenacházíš se dostatečně blízko. Ověř si, že jsi na správném místě. (Jsi přiližně {round(distance_in_m)} metrů daleko.)")
        else:
            if point.picked_up.count() == point.max_number_of_visits:
                Logs.objects.create(
                    player=request.user.player,
                    brief="point",
                    log=f"Hráč se pokusil sebrat point {submit_point_form.cleaned_data['point_id']}, ten už byl vybraný",
                )
                messages.error(request,
                               f"Point nemohl být ověřen. Už byl před tebou navštíven {point.max_number_of_visits}/{point.max_number_of_visits} lidí")
            else:
                point.picked_up.add(request.user.player)
                point.save()
                Logs.objects.create(
                    player=request.user.player,
                    brief="point",
                    log=f"Hráč sebral point {submit_point_form.cleaned_data['point_id']}",
                )
                messages.info(request,
                              f"Point úspěšně ověřen. Je teď navštíven {point.picked_up.count()}/{point.max_number_of_visits} lidí")

        return redirect('/')
    return index(request, submit_point_form=submit_point_form)


def rules(request):
    return render(request=request, template_name="hg_app/rules.html")


def stats(request):
    kills = request.user.player.my_kills.all()
    packages = Package.objects.filter(picked_up=request.user.player)
    points = Point.objects.filter(picked_up__user_id__in=[request.user.id])
    deaths = request.user.player.my_deaths.all()
    return render(request=request, template_name="hg_app/stats.html", context=locals())


def players(request):
    players = Player.objects.exclude(user=request.user).exclude(lives=0).order_by('user__username')
    dead_players = Player.objects.filter(lives=0).order_by('user__username')
    return render(request=request, template_name="hg_app/players.html", context=locals())

def player_location(request):
    assert request.method == 'GET'
    if request.user.is_authenticated:
        long = request.GET['long']
        lat = request.GET['lat']
        point = GPoint(float(long), float(lat), srid=4326)
        request.user.player.location_history = point
        request.user.player.save()
    return HttpResponse("Success!")

def submit_special(request):
    if not request.method == "POST":
        return redirect('/')

    submit_special_form = SubmitSpecial(request.POST)

    if submit_special_form.is_valid():
        verification_code = submit_special_form.cleaned_data['verification_code']
        player = request.user.player

        print(list(SpecialAction.objects.exclude(used=True).values_list('verification_code', flat=True)))
        if verification_code not in list(SpecialAction.objects.values_list('verification_code', flat=True)):
            Logs.objects.create(
                player=request.user.player,
                brief="special",
                log=f"Hráč se pokusil odeslat neexistující speciální efekt",
            )
            messages.error(request,f"Tento kód nepatří k žádnému bonusu")
            return redirect('/')

        special_action = SpecialAction.objects.get(verification_code=verification_code)
        if special_action.used:
            Logs.objects.create(
                player=request.user.player,
                brief="special",
                log=f"Hráč se pokusil odeslat speciální efekt {special_action}, který už někdo použil",
            )
            messages.error(request, f"Kód byl již jednou použit.")
            return redirect('/')
        if special_action.effect == "trofej":
            player.trophy_count += 1
            Logs.objects.create(
                player=request.user.player,
                brief="special",
                log=f"Hráči byla přidána trofej speciálním efektem {special_action}",
            )
            messages.info(request, f"Kód úspěšně ověřen. Byla ti přidána trofej.")
        elif special_action.effect == "zivot":
            if player.lives >= 3:
                Logs.objects.create(
                    player=request.user.player,
                    brief="special",
                    log=f"Hráč se pokusil přidat si životy speciálním efektem {special_action}, ale měl maximální počet",
                )
                messages.error(request,f"Maximální počet životů je 3. Nech si kód na později.")
                return redirect("/")
            player.lives += 1
            Logs.objects.create(
                player=request.user.player,
                brief="special",
                log=f"Hráči byl přidán život speciálním efektem {special_action}",
            )
            messages.info(request, f"Kód úspěšně ověřen. Byl ti přidán jeden život.")
        player.save()
        special_action.used = True
        special_action.save()
        return redirect('/')

@login_required
def account(request, password_change_form=None, profile_picture_form=None):
    if request.user.is_authenticated:
        if password_change_form is None:
            password_change_form = PasswordChangeForm(request.user)
        if profile_picture_form is None:
            profile_picture_form = ProfilePicture()

    user = request.user

    return render(request=request, template_name='hg_app/account.html', context=locals())

@login_required
def change_password(request):
    if request.method == "POST":
        password_change_form = PasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tvoje heslo bylo úspěšně změněno')
            return redirect('/account')
        else:
            messages.error(request, "Změna hesla selhala.")
    else:
        password_change_form = PasswordChangeForm(request.user)

    return account(request, password_change_form=password_change_form)

@login_required
def profile_picture(request):
    if request.method == "POST":
        profile_picture_form = ProfilePicture(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            request.user.player.photo = profile_picture_form.cleaned_data['photo']
            request.user.player.save()
            messages.success(request, 'Profilový obrázek byl úspěšně nahrán')
            return redirect('/account')
        else:
            messages.error(request, "Změna profilového obrázku selhala.")
    else:
        profile_picture_form = ProfilePicture()

    return account(request, profile_picture_form=profile_picture_form)


@login_required
def epic_map(request):
    if not request.user.is_superuser:
        raise PermissionDenied()
    players_alive = Player.objects.exclude(lives=0).exclude(location_history__isnull=True)
    players_dead = Player.objects.filter(lives=0).exclude(location_history__isnull=True)
    packages_picked_up = Package.objects.filter(picked_up__isnull=False)
    packages_free = Package.objects.filter(picked_up__isnull=True)
    points_picked_up = Point.objects.annotate(num=Count('picked_up')).filter(num=F('max_number_of_visits'))
    points_free = Point.objects.annotate(num=Count('picked_up')).exclude(num=F('max_number_of_visits'))
    end_game = AdminConfiguration.objects.get(id=1).end_game

    return render(request, template_name="hg_app/epic_map.html", context=locals())
