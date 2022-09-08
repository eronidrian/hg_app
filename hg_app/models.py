from django.db import models
from json import dumps, loads
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point as P
from random import randint


class Package(models.Model):
    location = models.PointField(srid=4326, null=True, blank=True, verbose_name='Poloha')
    description = models.CharField(max_length=100, blank=True, verbose_name='Popis')
    opening_time = models.DateTimeField(verbose_name='Čas otevření')
    picked_up = models.ForeignKey('Player', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Sebráno')

    def __str__(self):
        return f"Balíček #{self.id}"

    class Meta:
        ordering = '-opening_time',
        verbose_name = 'Balíček'
        verbose_name_plural = 'Balíčky'


class Point(models.Model):
    location = models.PointField(srid=4326, null=True, blank=True, verbose_name='Poloha')
    description = models.CharField(max_length=100, blank=True, verbose_name='Popis')
    opening_time = models.DateTimeField(verbose_name='Čas otevření')
    picked_up = models.ManyToManyField('Player', blank=True, verbose_name='Navštíveno')
    max_number_of_visits = models.IntegerField(default=0, verbose_name='Maximální počet návštěv')

    def __str__(self):
        return f"Bod #{self.id}"

    class Meta:
        ordering = '-opening_time',
        verbose_name = 'Bod'
        verbose_name_plural = 'Body'


class Message(models.Model):
    text = models.CharField(max_length=300, verbose_name='Obsah zprávy')
    brief = models.CharField(max_length=20, verbose_name='Stručně')
    time = models.DateTimeField(verbose_name='Čas zobrazení')
    players = models.ManyToManyField('Player', blank=True, verbose_name='Pro hráče')

    def __str__(self):
        return self.brief

    class Meta:
        ordering = '-time',
        verbose_name = 'Zpráva'
        verbose_name_plural = 'Zprávy'


class Kill(models.Model):
    victim = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='my_deaths', verbose_name='Oběť')
    murderer = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='my_kills', verbose_name='Útočník')
    stealth_kill = models.BooleanField(default=False)
    time = models.TimeField(auto_now=True, verbose_name='Čas')
    quest_kill = models.BooleanField(default=False)
    trophy_kill = models.BooleanField(default=False)

    def __str__(self):
        return f"Hráč {self.victim} byl zabit hráčem {self.murderer}"

    class Meta:
        verbose_name = 'Kill'
        verbose_name_plural = 'Killy'


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player', verbose_name='Uživatel')
    lives = models.IntegerField(default=3, verbose_name='Životy')
    points = models.ManyToManyField(Point, blank=True, verbose_name='Pointy')
    packages = models.ManyToManyField(Package, blank=True, verbose_name='Balíčky')
    score = models.IntegerField(default=0, verbose_name='Skóre')
    photo = models.ImageField(upload_to='photos', blank=True, verbose_name='Fotka')
    location_history = models.PointField(verbose_name='Historie polohy', blank=True, null=True, srid=4326)
    trophy_count = models.IntegerField(default=0, verbose_name='Počet trofejí')
    quest = models.ForeignKey('Player', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Hráč'
        verbose_name_plural = 'Hráči'


def random_string():
    return str(randint(10000, 99999))


class SpecialAction(models.Model):
    used = models.BooleanField(default=False, verbose_name="Použito")
    effect_choices = [("zivot", "zivot"),
                      ("trofej", "trofej")]
    effect = models.CharField(verbose_name="Efekt", choices=effect_choices, max_length=30)
    verification_code = models.CharField(default=random_string, max_length=20, verbose_name="Ověřovací kód")

    def __str__(self):
        return f"Speciální efekt {self.effect} #{self.id}"

    class Meta:
        verbose_name = 'Speciální akce'
        verbose_name_plural = 'Speciální akce'


class AdminConfiguration(models.Model):
    max_distance_from_point = models.IntegerField(default=50, verbose_name="Jak daleko musí být hráč od pointu (metry)")
    stealth_score = models.IntegerField(default=7, verbose_name="Body za stealth kill")
    kill_score = models.IntegerField(default=5, verbose_name="Body za normální kill")
    point_score = models.IntegerField(default=3, verbose_name="Body za point")
    quest_score = models.IntegerField(default=3, verbose_name="Body navíc za quest")
    show_people = models.BooleanField(default=False, verbose_name="Odkrýt pozice všech hráčů")
    turn_off = models.BooleanField(default=False, verbose_name="Vypnout aplikaci pro hráče")
    hide_after = models.IntegerField(default=3, verbose_name="Schovat vybrané pointy/balíčky za (hodiny)")

    class Meta:
        verbose_name = "Nastavení"
        verbose_name_plural = "Nastavení"

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Nastavení herních konstant"


class Logs(models.Model):
    time = models.TimeField(auto_now=True, verbose_name='Čas')
    player = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Hráč")
    brief = models.CharField(max_length=10, verbose_name='Stručně')
    log = models.CharField(max_length=100, verbose_name='Obsah logu')

    class Meta:
        ordering = 'time',
        verbose_name = "Log"
        verbose_name_plural = "Logy"

    def __str__(self):
        return f"{self.time}"
