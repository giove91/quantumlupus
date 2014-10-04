from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.forms import *

from game.models import *
import localization as qwl
import ruleset as qwr
import time


#################
#	Util		#
#################

class InfoObj:
	def __init__(self, **kwargs):
		for key, value in kwargs.iteritems():
			setattr(self, key, value)

#################
#	Forms		#
#################


class GameForm(Form):
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		dic = qwl.lang(user.setting.lang)
		Form.__init__(self, *args, **kwargs)
		self.fields['name'] = CharField(min_length=3,max_length=256,required=True,initial=qwl.randgame(),label='Nome del villaggio:')
		self.fields['password'] = CharField(max_length=256,initial='',required=False,label='Parola d\'ordine:')
		self.fields['allow_dup' ] = BooleanField(initial=False,required=False,label='Consenti personaggi multipli per giocatore')
		self.fields['tie_draw' ] = BooleanField(initial=False,required=False,label='Sorteggia se parit\xc3\xa0')
		self.fields['tie_play_off' ] = BooleanField(initial=False,required=False,label='Spareggio su pareggio')
		self.fields['tie_conclave' ] = BooleanField(initial=False,required=False,label='La votazione prosegue arbitrariamente')
		self.fields['limit_day'] = IntegerField(min_value=10,initial=None,required=False,label='Tempo limite diurno:')
		self.fields['limit_night'] = IntegerField(min_value=10,initial=None,required=False,label='Tempo limite notturno:')
		self.fields['max_players'] = IntegerField(min_value=2,initial=None,required=False,label='Massimo numero di giocatori consentito:')
		self.fields['max_states'] = IntegerField(min_value=1,max_value=1000000,initial=1000000,required=True,label='Massimo numero di stati iniziali generati:')

class PlayForm(Form):
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		dic = qwl.lang(user.setting.lang)
		Form.__init__(self, *args, **kwargs)
		self.fields['name'] = CharField(min_length=3,max_length=256,required=True,initial=qwl.randname(),label='nickname:')
		self.fields['game'] = ModelChoiceField(queryset=Game.objects.filter(day=0),required=True,initial=None,label='partita:')
		self.fields['password'] = CharField(max_length=256,initial='',required=False,label='passphrase:')

class DwellerForm(Form):
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		dic = qwl.lang(user.setting.lang)
		Form.__init__(self, *args, **kwargs)
		self.fields['role'] = ChoiceField(choices=[(i,dic('role[%d]' % i)) for i in xrange(qwr.ROLE_WEREWOLF+1)],required=True)
		self.fields['quantum' ] = BooleanField(initial=True,required=False,label='Quantum')
		self.fields['num'] = IntegerField(min_value=1,initial=1,required=True)

class ActionForm(Form):
	def __init__(self, *args, **kwargs):
		player = kwargs.pop('player', None)
		vote = kwargs.pop('vote', False)
		dic = qwl.lang(player.user.setting.lang)
		Form.__init__(self, *args, **kwargs)
		if vote:
			self.fields['target'] = ModelChoiceField(queryset=Player.objects.filter(game=player.game).exclude(pk=player.pk),required=True,label='Vota')
		else:
			acts = [(i,dic('action[%d]' % i)) for i in xrange(qwr.ROLE_WEREWOLF+1) if qwr.ROLE_DESC[i][1] in (qwr.ROLE_MEASURE,qwr.ROLE_TRANSFORM)]
			try:
				acts = [a for a in acts if Status.objects.get(player=player,role_id=a[0]).probability > 0]
			except:
				pass
			self.fields['action'] = ChoiceField(choices=acts,required=True)
			self.fields['target'] = ModelChoiceField(queryset=Player.objects.filter(game=player.game).exclude(pk=player.pk),required=True)


#################
#	Views		#
#################


def logout_view(request):
	logout(request)
	return redirect('index')


class IndexView(View):
	def post(self, request):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		if request.POST['type'] == 'subscribe':
			form = PlayForm(request.POST,user=user)
			if 'details' in form.data:
				if form.is_valid():
					return redirect('settings',form.cleaned_data['game'].pk)
			if form.is_valid():
				game = form.cleaned_data['game']
				if form.cleaned_data['password'] == game.password and (game.max_players is None or len(Player.objects.filter(game=game)) < game.max_players):
					Player.objects.create(user=user,name=form.cleaned_data['name'],game=form.cleaned_data['game'])
				else:
					return HttpResponseForbidden("#01: Subscription denied: wrong password or maximum number of players reached.")
			return self.get(request)
		if request.POST['type'] == 'removeplayer':
			pid = int(request.POST['data'])
			try:
				player = Player.objects.get(pk=pid)
			except:
				return self.get(request)
			if player.user != user:
				return HttpResponseForbidden("403: Access denied.")
			player.delete()
			return self.get(request)
		if request.POST['type'] == 'removegame':
			gid = int(request.POST['data'])
			try:
				game = Game.objects.get(pk=gid)
			except:
				return self.get(request)
			if game.admin != user or game.day > 0:
				return HttpResponseForbidden("403: Access denied.")
			Player.objects.filter(game=game).delete()
			Character.objects.filter(game=game).delete()
			game.delete()
			return self.get(request)

	def get(self, request):
		user = request.user
		dic = qwl.lang(user.setting.lang)
	
		pls = Player.objects.filter(user=user)
		pls = [InfoObj(game=p.game.name, plyr=p.name, pid=p.pk, waiting=p.game.day<1) for p in pls]
		gms = Game.objects.filter(admin=user).exclude(day=-1)
		gms = [InfoObj(name=g.name, id=g.pk, waiting=g.day<1) for g in gms]
		context = {
			'im_logged': user is not None,
			'plays': pls,
			'games': gms,
			'newplay': PlayForm(user=user),
		}
		return render(request, 'index.html', context)


class NewView(View):
	def post(self, request):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		if user is None:
			return render(request, 'unauthorized.html')
		form = GameForm(request.POST,user=user)
		if form.is_valid():
			g = Game.objects.create(name=form.cleaned_data['name'],password=form.cleaned_data['password'],admin=user,allow_dup=form.cleaned_data['allow_dup'],tie_draw=form.cleaned_data['tie_draw'],tie_play_off=form.cleaned_data['tie_play_off'],tie_conclave=form.cleaned_data['tie_conclave'],limit_day=form.cleaned_data['limit_day'],limit_night=form.cleaned_data['limit_night'],max_players=form.cleaned_data['max_players'],max_states=form.cleaned_data['max_states'])
			return redirect('settings',g.pk)
		return self.get(request)

	def get(self, request):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		context = {
			'newgame': GameForm(user=user),
		}
		return render(request, 'new.html', context)


class SettingsView(View):
	def post(self, request, game_id):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		game = Game.objects.get(pk=game_id)
		
		if request.POST['type'] == 'add':
			if game.admin != user:
				return HttpResponseForbidden("403: Access denied.")
			form = DwellerForm(request.POST,user=user)
			if form.is_valid():
				for i in xrange(form.cleaned_data['num']):
					Character.objects.create(game=game,role_id=form.cleaned_data['role'],is_quantum=form.cleaned_data['quantum'])
			return self.get(request, game_id)
		if request.POST['type'] == 'remove':
			role_id = int(request.POST['data'])
			if role_id == 0 or game.admin != user:
				return HttpResponseForbidden("403: Access denied.")
			Character.objects.filter(game=game,role_id=abs(role_id)-1,is_quantum=role_id>0).delete()
			return self.get(request, game_id)
		if request.POST['type'] == 'start':
			game.day = 1
			game.save()
			return self.get(request, game_id)
		if request.POST['type'] == 'stop':
			game.day = -1
			game.save()
			return redirect('index')

	def get(self, request, game_id, message=None):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		game = Game.objects.get(pk=game_id)
		if game.day < 0:
			return HttpResponseForbidden("403: Access denied.")
		dws = []
		for i in xrange(qwr.ROLE_WEREWOLF+1):
			for q in (True,False):
				n = len(Character.objects.filter(game=game,role_id=i,is_quantum=q))
				if n > 0:
					dws.append(InfoObj(text=('%d %s (%s)' % (n, dic('role[%d]' % i).lower(), 'quantum' if q else 'standard')),id=(i+1)*(1 if q else -1)))
		pls = Player.objects.filter(game=game)
		pls = [[p.name, '(' + p.user.username + ')'] for p in pls]
		stg = ('sorteggio,' if game.tie_draw else '')+('spareggio,' if game.tie_play_off else '')+('conclave,' if game.tie_conclave else '')
		if len(stg) == 0:
			stg = 'standard,'
		stg = stg[:-1]
		stg = [('Admin:',game.admin.username),('Consenti doppioni:','vero' if game.allow_dup else 'falso'),('Votazione:',stg)]
		if game.limit_day is not None:
			stg += [('Limite giorno:',str(game.limit_day) + ' sec')]
		if game.limit_night is not None:
			stg += [('Limite notte:',str(game.limit_night) + ' sec')]
		if game.max_players is not None:
			stg += [('Limite giocatori:',game.max_players)]
		if game.max_states is not None:
			stg += [('Limite stati:',game.max_states)]
		context = {
			'game_id': game_id,
			'game': game.name,
			'im_admin': game.admin == user,
			'game_waiting': game.day == 0,
			'day': dic('phase[%d] %d' % (game.phase, game.day)),
			'settings': stg,
			'dwellers': dws,
			'players': pls,
			'newdweller': DwellerForm(user=user),
		}
		return render(request, 'settings.html', context)


class PlayView(View):
	def post(self, request, player_id):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		player = Player.objects.get(pk=player_id)
		if player.user != user:
			return HttpResponseForbidden("403: Access denied.")

		form = ActionForm(request.POST, player=player, vote=player.game.phase != qwr.PHASE_NIGHT)
		if form.is_valid():
			if 'action' in form.cleaned_data:
				Action.objects.create(day=player.game.day,player=player,role_id=form.cleaned_data['action'],target=form.cleaned_data['target'])
			else:
				Action.objects.create(day=player.game.day,player=player,role_id=-player.game.phase,target=form.cleaned_data['target'])
		return self.get(request, player_id)

	def get(self, request, player_id, message=None):
		user = request.user
		dic = qwl.lang(user.setting.lang)
		player = Player.objects.get(pk=player_id)
		if player.user != user:
			return HttpResponseForbidden("403: Access denied.")
		if player.game.day == 0:
			return redirect('settings',player.game.pk)

		plogs = list(Log.objects.filter(player=player))
		plogs = reversed([[dic('[phase[%d] %d]\t' % (player.game.phase, player.game.day)), dic(t.content)] for t in plogs])
		glogs = Log.objects.filter(game=player.game)
		glogs = [dic(g.content,aslist=True) for g in glogs]
		pstat = Player.objects.filter(game=player.game)
		try:
			pstat = [ InfoObj(name=p.name, death=int(Status.objects.get(player=p,role_id=qwr.ROLE_DEAD).probability*100), day=int(Status.objects.get(player=p,role_id=None,friend=None).probability*10)/10.0, wolf=int(Status.objects.get(player=player,friend=p).probability*100)) for p in pstat]
		except:
			pstat = []
		rstat = Status.objects.filter(player=player).exclude(role_id=None)
		rstat = [[dic('role[%d]' % r.role_id),str(int(r.probability*100))+'%'] for r in rstat if r.probability > 0]
		context = {
			'village': dic('<VILLAGE "%s">' % player.game.name),
			'name': player.name,
			'countdown': player.game.countdown - int(time.time()),
			'game_running': player.game.day > 0,
			'day': dic('phase[%d] %d' % (player.game.phase, player.game.day)),
			'plogs': plogs,
			'glogs': glogs,
			'playerstat': pstat,
			'rolestat': rstat,
			'newact': ActionForm(player=player, vote=player.game.phase != qwr.PHASE_NIGHT),
			'player_id': player_id,
		}
		return render(request, 'play.html', context)
