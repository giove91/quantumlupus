from django.conf.urls import patterns, url
from django.contrib.auth.decorators import user_passes_test

from game.views import *


urlpatterns = patterns('',
    url(r'^index/$', IndexView.as_view(), name='index'),
    url(r'^new/$', NewView.as_view(), name='new'),
    url(r'^settings/(?P<game_id>\d+)/$', SettingsView.as_view(), name='settings'),
    url(r'^play/(?P<player_id>\d+)/$', PlayView.as_view(), name='play'),
)
