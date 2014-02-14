from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic.base import View
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core import exceptions

from django import forms

from django.contrib.auth.models import User
from game.models import *


def home(request):
    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    return redirect(home)


class StatusView(View):
    def get(self, request, player_id):
        
        user = request.user
        player = Player.objects.get(pk=player_id)
        
        if player.user != user:
            return render(request, 'index.html')
        
        
        logs = Log.objects.filter(player=player)
        
        context = {
            'player_id': player_id,
            'logs': logs,
        }   
        return render(request, 'status.html', context)

