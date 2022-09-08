from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import *


class MyKillsAdmin(admin.TabularInline):
    model = Kill
    fk_name = 'murderer'

    verbose_name = 'Hráčův kill'
    verbose_name_plural = 'Hráčovy killy'


class MyDeathsAdmin(admin.TabularInline):
    model = Kill
    fk_name = 'victim'

    verbose_name = 'Hráčova smrt'
    verbose_name_plural = 'Hráčovy smrti'


@admin.register(Point)
class PointAdmin(OSMGeoAdmin):
    default_lon = 46
    default_lat = 17
    default_zoom = 15


@admin.register(Package)
class PackageAdmin(OSMGeoAdmin):
    default_lon = 46
    default_lat = 17
    default_zoom = 15


@admin.register(Player)
class PlayerAdmin(OSMGeoAdmin):
    search_fields = 'user__username',
    list_display = 'user', 'lives', 'score'
    list_filter = 'lives',

    filter_horizontal = 'points','packages'

    inlines = [MyKillsAdmin, MyDeathsAdmin]


admin.site.register(Kill)


admin.site.register(SpecialAction)
admin.site.register(AdminConfiguration)

@admin.register(Logs)
class LogsAdmin(admin.ModelAdmin):
    list_display = 'player', 'brief', 'log'
    list_filter = 'player',
