from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey('Game')


class Game(models.Model):
    name = models.CharField(max_length=256)
    password = models.CharField(max_length=256, null=True, blank=True)
    admin = models.ForeignKey(User)
    
    day = models.IntegerField(default=0)
    phase = models.IntegerField(default=1)
    countdown = models.IntegerField(null=True, blank=True)
    limit_day = models.IntegerField(null=True, blank=True)
    limit_night = models.IntegerField(null=True, blank=True)
    max_players = models.IntegerField(null=True, blank=True)
    max_states = models.IntegerField(null=True, blank=True)
    tie_draw = models.BooleanField(default=False)
    tie_play_off = models.BooleanField(default=False)
    tie_conclave = models.BooleanField(default=False)
    seed = models.IntegerField(default=0)


class Village(models.Model):
    game = models.ForeignKey(Game)
    role_id = models.IntegerField()
    is_quantum = models.BooleanField(default=False)
    num = models.IntegerField(default=1)


class Status(models.Model):
    player = models.ForeignKey(Player)
    probability = models.FloatField()
    
    status_type = models.IntegerField()
    role_id = models.IntegerField(null=True, blank=True)
    friend = models.ForeignKey(Player, related_name='+')
    
    class Meta:
        verbose_name_plural = "status"


class Action(models.Model):
    day = models.IntegerField()
    player = models.ForeignKey(Player)
    role_id = models.IntegerField()
    target = models.ForeignKey(Player, related_name='+')


class Log(models.Model):
    day = models.IntegerField()
    player = models.ForeignKey(Player)
    content = models.CharField(max_length=256)


