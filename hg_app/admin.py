from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import *


class MyKillsAdmin(admin.TabularInline):
    model = Kill
    fk_name = 'murderer'

    verbose_name = 'My kill'
    verbose_name_plural = 'My kills'


class MyDeathsAdmin(admin.TabularInline):
    model = Kill
    fk_name = 'victim'

    verbose_name = 'My death'
    verbose_name_plural = 'My deaths'


@admin.register(Point)
class PointAdmin(OSMGeoAdmin):
    default_lon = 46
    default_lat = 17
    default_zoom = 15



@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = 'user__username',
    list_display = 'user', 'lives', 'score'
    list_filter = 'lives',

    filter_horizontal = 'points',

    inlines = [MyKillsAdmin, MyDeathsAdmin]


admin.site.register(Package)
admin.site.register(Kill)
admin.site.register(Message)
