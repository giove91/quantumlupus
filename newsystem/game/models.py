from django.db import models
from django.contrib.auth.models import User
import localization as qwl
import ruleset as qwr

dic = qwl.lang('it')


class Setting(models.Model):
	user = models.OneToOneField(User)
	avatar = models.IntegerField(default=0)
	lang = models.CharField(max_length=256)
	won = models.IntegerField(default=0)
	lost = models.IntegerField(default=0)
#    level = models.IntegerField(default=0)
	def __unicode__(self):
		return unicode(self.user.username)


class Game(models.Model):
	name = models.CharField(max_length=256)
	password = models.CharField(max_length=256, null=True, blank=True)
	admin = models.ForeignKey(User)
#    theme = models.IntegerField(default=0)

	allow_dup = models.BooleanField(default=False)
	tie_draw = models.BooleanField(default=False)
	tie_play_off = models.BooleanField(default=False)
	tie_conclave = models.BooleanField(default=False)
#    wolf_vote = models.IntegerField(default=0)
	limit_day = models.IntegerField(null=True, blank=True)
	limit_night = models.IntegerField(null=True, blank=True)
	max_players = models.IntegerField(null=True, blank=True)
	max_states = models.IntegerField(null=True, blank=True)

	day = models.IntegerField(default=0)
	phase = models.IntegerField(default=0)
	countdown = models.IntegerField(null=True, blank=True)
	seed = models.IntegerField(default=0)
	def __unicode__(self):
		return unicode(self.name)


class Player(models.Model):
	name = models.CharField(max_length=256)
	user = models.ForeignKey(User)
	game = models.ForeignKey(Game)
	def __unicode__(self):
		return unicode(self.name)


class Character(models.Model):
	game = models.ForeignKey(Game)
	role_id = models.IntegerField()
	is_quantum = models.BooleanField(default=False)
	def __unicode__(self):
		return unicode('%s: %s %s' % (self.game.name, dic('role[%d]' % self.role_id).lower(), 'quantum' if self.is_quantum else 'standard'))


class Action(models.Model):
	day = models.IntegerField()
	player = models.ForeignKey(Player)
	role_id = models.IntegerField()
	target = models.ForeignKey(Player, related_name='+')
	def __unicode__(self):
		return unicode('(Day%d) %s %s %s' % (self.day, self.player.name, dic('action[%d]' % self.role_id).lower() if self.role_id > 0 else 'vota', self.target.name))


class Log(models.Model):
	day = models.IntegerField()
	player = models.ForeignKey(Player, null=True, blank=True)
	game = models.ForeignKey(Game, null=True, blank=True)
	content = models.TextField()
	def __unicode__(self):
		return unicode('(Day%d) %s: "%s"' % (self.day, self.player.name if self.player is not None else self.game.name, unicode(dic(self.content),'utf-8') ))


class Status(models.Model):
	player = models.ForeignKey(Player)
	probability = models.FloatField(default=0)
	role_id = models.IntegerField(null=True, blank=True)
	friend = models.ForeignKey(Player, null=True, blank=True, related_name='+')
	def __unicode__(self):
		if self.role_id is not None:
			return unicode('PROBABILITY(%s %s) = %f' % (self.player.name, dic('role[%d]' % self.role_id).lower(), self.probability))
		if self.friend is not None:
			return unicode('PROBABILITY(%s %s | %s %s) = %f' % (self.friend.name, dic('role[%d]' % qwr.ROLE_WEREWOLF).lower(), self.player.name, dic('role[%d]' % qwr.ROLE_WEREWOLF).lower(), self.probability))
		return unicode('AVERAGEDEATH(%s) = %f' % (self.player.name, self.probability))
	class Meta:
		verbose_name_plural = "status"
