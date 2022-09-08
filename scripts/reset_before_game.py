from hg_app.models import *

for player in Player.objects.all():
    player.lives = 3
    packages = Package.objects.get(description="TEST")
    player.packages.remove(*packages)
    points = Point.objects.get(description="TEST")
    player.points.remove(*points)
    player.trophy_count = 0
    player.score = 0

