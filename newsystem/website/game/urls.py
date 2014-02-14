from django.conf.urls import patterns, url
from django.contrib.auth.decorators import user_passes_test

from game.views import *


urlpatterns = patterns('',
    url(r'^setup/$', home, name='setup'),
    url(r'^status/(?P<player_id>\d+)/$', StatusView.as_view(), name='status')
)

