from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from hg_app.models import *
from .values import *

@receiver(post_save, sender=User)
def create_player(instance, created, **kwargs):
    if created:
        Player.objects.create(
            user=instance
        )


@receiver(post_save, sender=Kill)
def remove_live(instance, created, **kwargs):
    if created:
        victim = instance.victim
        victim.lives -= 1
        victim.save()


@receiver(post_save, sender=Kill)
def add_score_kill(instance, created, **kwargs):
    if created:
        murderer = instance.murderer
        if instance.stealth_kill:
            murderer.score += STEALTH_SCORE
        else:
            murderer.score += KILL_SCORE
        murderer.save()


@receiver(m2m_changed, sender=Point.picked_up.through)
def add_score_point(instance, pk_set, action, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            player = Player.objects.get(id=pk)
            player.score += POINT_SCORE
            player.save()



# @receiver(post_save, sender=Package)
# def add_package_message(instance, created, **kwargs):
#     if created:
#         Message.objects.create(
#             text=f"Balíček #{instance.id} se otevírá v {instance.opening_time.strftime('%H:%M')} na souřadnicích {instance.lat}N, {instance.long}E",
#             brief="Otevírá se balíček",
#             time=instance.opening_time
#         )

