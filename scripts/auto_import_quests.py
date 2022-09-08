from hg_app.models import *
import random
import csv


def choose_random_player(murderer, victim=None):
    if victim is not None:
        choose_from = Player.objects.exclude(lives=0).exclude(user=murderer.user).exclude(user=victim.user)
    else:
        choose_from = Player.objects.exclude(lives=0).exclude(user=murderer.user)
    random_index = random.randint(0, len(choose_from) - 1)
    return choose_from[random_index]


for player in Player.objects.all():
    player.quest = choose_random_player(player)
    player.save()