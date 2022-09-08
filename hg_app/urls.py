from django.urls import path, include
from . import views
from hg import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("submit_kill/", views.submit_kill, name="submit_kill"),
    path("submit_package/", views.submit_package, name="submit_package"),
    path("rules/", views.rules, name="rules"),
    path("stats/", views.stats, name="stats"),
    path("players/", views.players, name="players"),
    path("submit_point/", views.submit_point, name="submit_point"),
    path("player_location/", views.player_location, name="player_location"),
    path("submit_special/", views.submit_special, name="submit_special"),
    path("account/", views.account, name="account"),
    path("account/change_password", views.change_password, name="change_password"),
    path("account/profile_picture", views.profile_picture, name="profile_picture")
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
