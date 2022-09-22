import random

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from django.conf import settings

from hg_app.models import *

@receiver(post_save, sender=User)
def create_player(instance, created, **kwargs):
    if created:
        player = Player.objects.create(
            user=instance
        )


@receiver(post_save, sender=Kill)
def remove_live(instance, created, **kwargs):
    if created:
        victim = instance.victim
        victim.lives -= 1

        victim.save()


@receiver(post_save, sender=Kill)
def add_score_kill_pass_trophy(instance, created, **kwargs):
    if created:
        murderer = instance.murderer
        victim = instance.victim
        conf = AdminConfiguration.objects.get(id=1)
        if instance.stealth_kill:
            murderer.score += conf.stealth_score*(2**murderer.trophy_count)
        else:
            murderer.score += conf.kill_score*(2**murderer.trophy_count)
        if murderer.quest == victim:
            murderer.score += conf.quest_score*(2**murderer.trophy_count)
            murderer.quest = choose_random_player(murderer, victim)
            instance.quest_kill = True
        if murderer.trophy_count > 0:
            instance.trophy_kill = True
        if victim.trophy_count > 0:
            victim.trophy_count -= 1
            murderer.trophy_count += 1
            victim.save()
        murderer.save()
        instance.save()

@receiver(m2m_changed, sender=Point.picked_up.through)
def add_score_point(instance, pk_set, action, **kwargs):
    if action == "post_add":
        conf = AdminConfiguration.objects.get(id=1)
        for pk in pk_set:
            player = Player.objects.get(id=pk)
            player.score += conf.point_score*(2**player.trophy_count)
            player.save()


def choose_random_player(murderer, victim=None):
    if victim is not None:
        choose_from = Player.objects.exclude(lives=0).exclude(user=murderer.user).exclude(user=victim.user)
    else:
        choose_from = Player.objects.exclude(lives=0).exclude(user=murderer.user)
    random_index = random.randint(0, len(choose_from) - 1)
    return choose_from[random_index]
