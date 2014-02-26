#!/usr/bin/env pypy

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "website.server_settings"
import django
from django.contrib.auth.models import User
from game.models import *
import game.ruleset as qwr

import sys, random, time, re

#################################
#	utils						#
#################################

def randiff(N,v):
	if len(v) >= N or len(v) == 0:
		return random.randint(0,N-1)
	r = v[0]
	while r in v:
		r = random.randint(0,N-1)
	return r


#################################
#	permutations				#
#################################

def num_permutation(s, start):
	n   = len(s) - start
	tot = n
	rip = 1
	for i in xrange(start + 1, len(s)):
		n -= 1
		tot *= n
		if s[i] == s[i-1]:
			rip += 1
		else:
			rip = 1
		tot /= rip
	return tot

def random_permutation(s, start):
	for i in reversed(xrange(start + 1, len(s))):
		j = random.randint(start, i)
		s[i], s[j] = s[j], s[i]

def next_permutation(s, start):
	for i in reversed(xrange(start + 1, len(s))):
		if s[i] > s[i-1]:
			break
	else:
		return False
	i -= 1
	for j in reversed(xrange(i + 1, len(s))):
		if s[j] > s[i]:
			break
	s[i], s[j] = s[j], s[i]
	s[i + 1:] = reversed(s[i + 1:])
	return True


#################################
#	QuantumState				#
#################################

class QuantumState:
	# inizializza uno stato quantistico con certi ruoli e un massimo numero di stati
	def __init__(self,roles, max_states = 1000000):
		self.N = len(roles)
		self.day = 1
		self.quantum = []
		self.status = None
		self.end = None
		roles.sort()
		wolf = 0
		for i in roles:
			if abs(i) == qwr.ROLE_WEREWOLF:
				wolf += 1
		wolf = range(qwr.ROLE_WEREWOLF,qwr.ROLE_WEREWOLF+wolf)
		random.shuffle(wolf)
		for i in range(len(roles)):
			if abs(roles[i]) == qwr.ROLE_WEREWOLF:
				roles[i] = wolf.pop() * (1 if roles[i] > 0 else -1)
		roles.sort()
		for i in range(len(roles)):
			if roles[i] >= 0:
				break
		tot_states = num_permutation(roles,i)
		s = [abs(r) for r in roles]
		p = range(self.N)
		random.shuffle(p)
		if max_states < tot_states/4:
			nq = set()
			while (len(nq) < max_states):
				random_permutation(s,i)
				nq.add(tuple(s[p[j]] for j in xrange(self.N)))
			for s in nq:
				self.quantum.append([[x,0] for x in s])
		else:
			self.quantum.append([[s[p[j]],0] for j in xrange(self.N)])
			while (next_permutation(s,i)):
				self.quantum.append([[s[p[j]],0] for j in xrange(self.N)])
			if max_states < len(self.quantum):
				self.quantum = random.sample(self.quantum, max_states)

	def __len__(self):
		return len(self.quantum)

	def __iadd__(self,n):
		self.clean()
		self.day += n
		return self
	
	def __getitem__(self,id):
		if self.status is not None:
			return self.status[id]
		self.clean()
		self.status = [[0, [0 for r in xrange(qwr.ROLE_WEREWOLF+2)], [0 for j in xrange(self.N)], 0] for id in xrange(self.N)]
		wolf = False
		good = False
		for s in self.quantum:
			for id in xrange(self.N):
				if s[id][1] & ~qwr.DEATH_NULL != 0 or s[id][0] == qwr.ROLE_DEAD:
					self.status[id][qwr.STATUS_ROLE][qwr.ROLE_DEAD] += 1
					self.status[id][qwr.STATUS_DEATHDAY] += s[id][1]
				else:
					if s[id][0] >= qwr.ROLE_WEREWOLF:
						wolf = True
					else:
						good = True
				if s[id][0] >= qwr.ROLE_WEREWOLF:
					self.status[id][qwr.STATUS_ROLE][qwr.ROLE_WEREWOLF] += 1
					if  s[id][1] & ~qwr.DEATH_NULL == 0 and not [0 for i in s if i[0]>=qwr.ROLE_WEREWOLF and i[0]<s[id][0] and i[1] & ~qwr.DEATH_NULL == 0]:
						self.status[id][qwr.STATUS_ROLE][qwr.ROLE_WEREWOLF+1] += 1
					for j in xrange(self.N):
						if s[j][0] >= qwr.ROLE_WEREWOLF:
							self.status[id][qwr.STATUS_WOLFRIEND][j] += 1
				elif abs(s[id][0]) != qwr.ROLE_DEAD:
					self.status[id][qwr.STATUS_ROLE][abs(s[id][0])] += 1
		if wolf == False:
			self.end = True
		if good == False:
			self.end = False
		return self.status[id]

	def __repr__(self):
		d = qwl.it
		r = [False for i in xrange(qwr.ROLE_WEREWOLF+1)]
		s = '%d states\n\nG Morte\tMorto\t' % len(self)
		for i in xrange(1,qwr.ROLE_WEREWOLF):
			for j in xrange(self.N):
				if self[j][qwr.STATUS_ROLE][i] > 0:
					r[i] = True
					s += '%s\t' % (d.roles[i] if len(d.roles[i]) < 8 else d.roles[i][:7])
					break
		s += 'Lupo'
		r[qwr.ROLE_DEAD] = True
		r[qwr.ROLE_WEREWOLF] = True
		for i in range(self.N):
			if self[i][qwr.STATUS_ROLE][qwr.ROLE_DEAD] > 0:
				t = [str((10*self[i][qwr.STATUS_DEATHDAY]/self[i][qwr.STATUS_ROLE][qwr.ROLE_DEAD])/10.0)]
			else:
				t = ['0']
			for j in xrange(qwr.ROLE_WEREWOLF+1):
				if r[j]:
					t += [str(100*self[i][qwr.STATUS_ROLE][j]/len(self))+'%']
			if self[i][qwr.STATUS_ROLE][-2] > 0:
				t += ['D:'+str(100*self[i][qwr.STATUS_ROLE][-1]/self[i][qwr.STATUS_ROLE][-2])+'%'] + [str(100*x/self[i][qwr.STATUS_ROLE][-2])+'%' for x in self[i][qwr.STATUS_WOLFRIEND]]
			s += '\n%s' % '\t'.join(t)
		return s

	def winner(self):
		l = self[0]
		if self.end is None:
			return self.end
		self.quantum = [random.choice(self.quantum)]
		self.status = None
		return self.end

	def clean(self):
		for r in xrange(qwr.ROLE_WEREWOLF):
			if qwr.ROLE_DESC[r][1] == qwr.ROLE_PASSIVE and r in [x[0] for x in self.quantum[0]]:
				for i in xrange(self.N):
					self.act(None,i,r,None)
		for s in self.quantum:
			for i in xrange(len(s)):
				if s[i][1] == qwr.DEATH_NULL:
					s[i][1] = 0
		self.status = None

	def filter(self, check):
		j = 0
		for i in xrange(len(self)):
			if check(self.quantum[i]):
				self.quantum[j] = self.quantum[i]
				self.quantum[j]
				j += 1
		if j == 0:
			return False
		self.quantum = self.quantum[:j]
		return True

	def lynch(self, n):
		if not self.filter(lambda s: s[n][1] == 0):
			return False
		role = random.choice(self.quantum)[n][0]
		self.filter(lambda s: s[n][0] == role)
		for s in self.quantum:
			s[n][1] = -self.day
		self.status = None
		return True

	def act(self, a, c, r, t):
		if qwr.ROLE_DESC[r][1] == qwr.ROLE_MEASURE:
			s = random.choice(self.quantum)
			if qwr.ROLE_DESC[r][3] == qwr.ERROR_NEVER or (s[c][0] == r and s[c][1] & ~qwr.DEATH_NULL == 0):
				res = qwr.ROLE_DESC[r][2](s,a,c,t,None)
			else:
				res = qwr.ROLE_DESC[r][2](s,a,c,randiff(self.N,[c]),None)
			if not self.filter(lambda s: s[c][0] != r or s[c][1] & ~qwr.DEATH_NULL != 0 or (qwr.ROLE_DESC[r][2](s,a,c,t,res)) == res):
				for s in self.quantum:
					s[c][1] = self.day
				return False
			return res
		if qwr.ROLE_DESC[r][1] == qwr.ROLE_TRANSFORM:
			for s in self.quantum:
				if min(s[c][0],qwr.ROLE_WEREWOLF) == r and s[c][1] & ~qwr.DEATH_NULL == 0:
					qwr.ROLE_DESC[r][2](s,c,t,self.day)
		if qwr.ROLE_DESC[r][1] == qwr.ROLE_PASSIVE:
			for s in self.quantum:
				if s[c][0] == r:
					qwr.ROLE_DESC[r][2](s,c,t,self.day)
		self.status = None


#################################
#	Village						#
#################################

class Village:
	# init the village to a certain game in the db
	def __init__(self, game):
		self.game = game
		if self.game.seed == 0:
			self.game.seed = int(time.time()) % 1000000
		random.seed(self.game.seed)

		self.roles = Character.objects.filter(game=self.game).order_by('pk')
		self.players = Player.objects.filter(game=self.game).order_by('pk')
		self.ballot = []
		if len(self.roles) > len(self.players):
			for r in self.roles[len(self.roles):]:
				r.delete()
			self.roles = self.roles[:len(self.players)]
		if len(self.roles) < len(self.players):
			for p in self.players[len(self.roles):]:
				p.delete()
			self.players = self.players[:len(self.roles)]
		self.roles = [r.role_id * (1 if r.is_quantum else -1) for r in self.roles]

		if self.game.limit_day is not None and self.game.limit_night is not None:
			self.game.countdown = int(time.time()) + self.game.limit_day + self.game.limit_night
		else:
			self.game.countdown = int(time.time()) + 1000000
		self.game.phase = qwr.PHASE_NIGHT
		self.game.save()

		self.state = QuantumState(self.roles,self.game.max_states)
		self.write_status()
		self.randstate = random.getstate()
	# the village is updated
	def __call__(self):
		random.setstate(self.randstate)
		if self.game.day < 0:
			return True
		if self.state.winner() is not None:
			self.game.day = -1
			self.game.save()
			return True
		a = [None for i in xrange(len(self.players))]
		if not self.read_actions(a) and time.time() < self.game.countdown:
			return False
		if self.game.phase == qwr.PHASE_NIGHT:
			self.apply(a)
			self.state += 1
			self.game.day = self.state.day
			self.game.phase = qwr.PHASE_DAY
			self.game.countdown = int(time.time()) + (1000000 if self.game.limit_day is None else self.game.limit_day)
			self.game.save()
			self.randstate = random.getstate()
			return False
		if not self.lynch(a):
			self.game.phase += 1
			self.game.countdown = int(time.time()) + (1000000 if self.game.limit_day is None else self.game.limit_day)
			self.game.save()
			return False
		self.game.phase = qwr.PHASE_NIGHT
		self.game.countdown = int(time.time()) + (1000000 if self.game.limit_night is None else self.game.limit_night)
		self.game.save()
		self.randstate = random.getstate()
		return False
	# legge le azioni appena svolte
	def read_actions(self, actions):
		d = {}
		for p in xrange(len(self.players)):
			d[self.players[p].pk] = p
		done = True
		for p in self.players:
			if self.game.phase == qwr.PHASE_NIGHT:
				actions[d[p.pk]] = [None for j in xrange(qwr.ROLE_WEREWOLF+1)]
				for i in Action.objects.filter(day=self.game.day,player=p,role_id__gt=0).order_by('pk'):
					actions[d[p.pk]][i.role_id] = d[i.target.pk]
				for i in xrange(qwr.ROLE_WEREWOLF+1):
					if qwr.ROLE_DESC[i][1] in [qwr.ROLE_MEASURE, qwr.ROLE_TRANSFORM] and actions[d[p.pk]][i] is None and self.state[d[p.pk]][qwr.STATUS_ROLE][i] > 0:
						done = False
			else:
				for i in Action.objects.filter(day=self.game.day,player=p,role_id=-self.game.phase).order_by('pk'):
					actions[d[p.pk]] = d[i.target.pk]
				if actions[d[p.pk]] is None:
					done = False
		return done
	# write the status of the village in table "status"
	def write_status(self):
		for i in xrange(len(self.players)):
			for j in xrange(qwr.ROLE_WEREWOLF+2):
				st, a = Status.objects.get_or_create(player=self.players[i],role_id=j)
				st.probability = self.state[i][qwr.STATUS_ROLE][j]/float(len(self.state))
				st.save()
			for j in xrange(len(self.players)):
				st, a = Status.objects.get_or_create(player=self.players[i],friend=self.players[j])
				st.probability = self.state[i][qwr.STATUS_WOLFRIEND][j]/float(len(self.state))
				st.save()
			st, a = Status.objects.get_or_create(player=self.players[i],role_id=None,friend=None)
			st.probability = self.state[i][qwr.STATUS_DEATHDAY]/float(len(self.state))
			st.save()
	# check the pool, lynch the winner and return false if tied
	def lynch(self, votes):
		res = [[1] for i in votes]
		for v in xrange(len(votes)):
			# solo in questo caso il voto e' valido
			if votes[v] is not None and (self.ballot == [] or votes[v] in self.ballot) and self.state[v][qwr.STATUS_ROLE][qwr.ROLE_DEAD] < len(self.state) and self.state[votes[v]][qwr.STATUS_ROLE][qwr.ROLE_DEAD] < len(self.state):
				res[votes[v]] += [v]
				res[votes[v]][0] += 1
		txt = [[res[i][0]-1,i] for i in xrange(len(res)) if res[i][0] > 1]
		txt.sort(reverse=True)
		txt = '|'.join(['%s:\t%d (%s)' % (self.players[v[1]].name,v[0],', '.join([self.players[i].name for i in res[v[1]][1:]])) for v in txt])
		win = [i for i in xrange(len(res)) if len(res[i]) == max(res)[0]]
		if len(win) > 1 and (self.game.tie_conclave or (self.game.tie_play_off and self.ballot == [])):
			if self.game.tie_play_off:
				self.ballot = win
			txt = '<BALLOT>|' + txt
			Log.objects.create(day=self.game.day,game=self.game,content=txt)
			return False
		if len(win) == 1 or self.game.tie_draw:
			win = random.choice(win)
			self.state.lynch(win)
			txt = '<LYNCH: "%s">|' % self.players[win].name + txt
		else:
			txt = '<NOLYNCH>|' + txt
		Log.objects.create(day=self.game.day,game=self.game,content=txt)
		return True
	# apply the actions taken by night
	def apply(self, actions):
		for p in xrange(qwr.PRIORITY_MAX):
			r = [i for i in xrange(qwr.ROLE_WEREWOLF+1) if qwr.ROLE_DESC[i][0] == p]
			l = [[[i,j,actions[i][j]] for j in r if actions[i][j] is not None] for i in xrange(len(self.players))]
			l = sum(l,[])
			random.shuffle(l)
			for i in l:
				if self.state[i[0]][qwr.STATUS_ROLE][i[1]] > 0:
					res = self.state.act(actions, i[0], i[1], i[2])
					txt = '<ACTION: "acted[%d]", "%s">' % (i[1], self.players[i[2]].name)
					if isinstance(res,bool):
						txt += '<TRUE>' if res else '<FALSE>'
					elif isinstance(res,int):
						txt += '<ID: "%s">' % self.players[res].name
					txt += '.'
					Log.objects.create(day=self.state.day,player=self.players[i[0]],content=txt)


#################################
#	Main						#
#################################

if __name__ == '__main__':
	villages = set()
	if len(sys.argv) > 1 and sys.argv[1] == '-c':
		print 'Clearing database...'
		Game.objects.all().delete()
		Player.objects.all().delete()
		Character.objects.all().delete()
		Action.objects.all().delete()
		Status.objects.all().delete()
		Log.objects.all().delete()
	print 'Cleaning database...'
	for g in Game.objects.filter(day__gt=0):
		g.day = 1
		g.phase = 0
		g.save()
		Log.objects.filter(game=g).delete()
		Log.objects.filter(player__game=g).delete()
		Status.objects.filter(player__game=g).delete()
	try:
		while True:
			for g in Game.objects.filter(day=1,phase=0):
				print 'Starting game "%s"...' % g.name
				villages.add(Village(g))
			for g in Game.objects.filter(day=-1):
				if len(Player.objects.filter(game=g)) == 0:
					print 'Clearing game "%s"...' % g.name
					Character.objects.filter(game=v.game).delete()
					Action.objects.filter(player__game=v.game).delete()
					Status.objects.filter(player__game=v.game).delete()
					Log.objects.filter(game=v.game).delete()
					Log.objects.filter(player__game=v.game).delete()
					g.delete()
			for v in list(villages):
				if v():
					print 'Game "%s" ended.' % g.name
					villages.remove(v)
	except KeyboardInterrupt:
		print '\nStopping server. Goodbye!'

#################################
#	Debug						#
#################################


if __name__ != '__main__':
	import game.localization as qwl


class dQS:
	def display(self,state):
		i = -3
		for l in repr(state).split('\n'):
			f = l
			if i == -1:
				f = '\t' + f + '\t\t' + '\t'.join([self.names[j] for j in range(state.N)])
			if i >= 0:
				f = self.names[i] + '\t' + f
			if len(f.split('\t')) > 22:
				print '\t'.join(f.split('\t')[:22])
			else:
				print f
			i += 1

	def __call__(self,N):
		d = qwl.lang('it')
		if isinstance(N,int):
			roles = [random.randint(-qwr.ROLE_WEREWOLF+1,qwr.ROLE_WEREWOLF-1) for i in range(N-N/3)] + [qwr.ROLE_WEREWOLF * (2*random.randint(0,1)-1) for i in range(N/3)]
		else:
			roles = N
			N = len(roles)
		print "Ruoli presenti:", roles
		state = QuantumState(roles,2000000)
		while True:
			print "\n--- notte %d ---" % state.day
			self.display(state)
			if state.winner() is not None:
				break
			a = [[None for j in range(qwr.ROLE_WEREWOLF+1)] for i in xrange(N)]
			l = []
			for p in xrange(qwr.PRIORITY_MAX):
				prol = [i for i in xrange(qwr.ROLE_WEREWOLF+1) if qwr.ROLE_DESC[i][0] == p]
				ll = sum([[[i,r] for i in xrange(N) if state[i][qwr.STATUS_ROLE][qwr.ROLE_DEAD] < len(state) and state[i][qwr.STATUS_ROLE][r] > 0] for r in prol],[])
				random.shuffle(ll)
				l += ll
			for x in l:
				a[x[0]][x[1]] = randiff(N,[x[0]])
			for x in l:
				print "%s ha %s %s" % (self.names[x[0]],d.actions[x[1]],self.names[a[x[0]][x[1]]]),
				res = state.act(a, x[0], x[1], a[x[0]][x[1]])
				if isinstance(res,bool):
					print "con esito", ('positivo' if res else 'negativo')
				elif isinstance(res,int):
					print "scoprendo", self.names[res]
				else:
					print
			state += 1
			print "\n--- giorno %d ---" % state.day
			self.display(state)
			if state.winner() is not None:
				break
			while True:
				r = random.randint(0,N-1)
				if state.lynch(r):
					print "\nLinciamo %s!!! Ammorteee" % self.names[r]
					break
		print
		print "Hanno vinto i %s!" % ('villici' if state.winner() else 'lupi')
		print "--- final day ---"
		self.display(state)

	def __init__(self):
		self.active  = [i for i in xrange(qwr.ROLE_WEREWOLF+1) if qwr.ROLE_DESC[i][1] in [qwr.ROLE_MEASURE,qwr.ROLE_TRANSFORM]]
		self.names = ['Ammalia','Brumo','Carna','Darlo','Elica','Fascio','Gorgo','Hanno','Iene','Lucca','Marcio','Nicolla','Orario','o','Quisto','Rodeo','Sana','Tiziamo','Uggio','Vanesio','Zorro']


class dDB:
	def __init__(self):
		villages = set()
		if len(sys.argv) > 1 and sys.argv[1] == '-c':
			print 'Clearing database...'
			Game.objects.all().delete()
			Player.objects.all().delete()
			Character.objects.all().delete()
			Action.objects.all().delete()
			Status.objects.all().delete()
			Log.objects.all().delete()
		print 'Cleaning database...'
		for g in Game.objects.filter(day__gt=0):
			g.day = 1
			g.phase = qwr.PHASE_DAY
			g.save()
			Log.objects.filter(game=g).delete()
			Log.objects.filter(player__game=g).delete()
			Status.objects.filter(player__game=g).delete()

	def __call__(self):
		d = qwl.lang('it')
		villages = set()
		try:
			while True:
				for g in Game.objects.filter(day=1,phase=qwr.PHASE_DAY):
					v = Village(g)
					print "\n===============================\nVillaggio %s" % g.name
					print "--- %s %d ---" % ('giorno' if v.game.phase != qwr.PHASE_NIGHT else 'notte', v.game.day)
					self.display(v)
					villages.add(v)
				for g in Game.objects.filter(day=-1):
					if len(Player.objects.filter(game=g)) == 0:
						print 'Clearing game "%s"...' % g.name
						Character.objects.filter(game=v.game).delete()
						Action.objects.filter(player__game=v.game).delete()
						Status.objects.filter(player__game=v.game).delete()
						Log.objects.filter(game=v.game).delete()
						Log.objects.filter(player__game=v.game).delete()
						g.delete()
				for v in list(villages):
					if v():
						print "\nHANNO VINTO I %s!\n" % ('VILLICI' if v.state.winner() else 'LUPI')
						print "--- final day ---"
						self.display(v)
						villages.remove(v)
					if v.phase == qwr.PHASE_DAY:
						for i in Log.objects.filter(day=v.game.day-1,player__game=v.game):
							print "[%s] %s" % (i.player.name, d(i.content))
					else:
						for i in Log.objects.filter(day=v.state.day,game=v.game):
							print d(i.content)
		except KeyboardInterrupt:
			print '\nStopping server.'

	def display(self,vill):
		i = -3
		for l in repr(vill.state).split('\n'):
			f = l
			if i == -1:
				f = '\t' + f + '\t\t' + '\t'.join([vill.players[j].name.split(' ')[0] for j in range(vill.state.N)])
			if i >= 0:
				f = vill.players[i].name.split(' ')[0] + '\t' + f
			if len(f.split('\t')) > 22:
				print '\t'.join(f.split('\t')[:22])
			else:
				print f
			i += 1

	def newgame(self,n):
		if isinstance(n,int):
			roles = [random.randint(-qwr.ROLE_WEREWOLF+1,qwr.ROLE_WEREWOLF-1) for i in range(n-n/3)] + [qwr.ROLE_WEREWOLF * (2*random.randint(0,1)-1) for i in range(n/3)]
			random.shuffle(roles)
		else:
			roles = n
			n = len(roles)
		users = User.objects.all()
		game = Game.objects.create(name=qwl.randgame(),password=qwl.randstr(),admin=random.choice(users),limit_day=0,limit_night=0,max_players=n,max_states=100000,tie_draw=random.choice([True,False]),tie_play_off=random.choice([True,False]),tie_conclave=random.choice([True,False]))
		for i in roles:
			Character.objects.create(game=game,role_id=abs(i),is_quantum=i>=0)
		for i in xrange(n):
			Player.objects.create(name=qwl.randname(),user=random.choice(users),game=game)
		players = list(Player.objects.filter(game=game))
		for i in xrange(20):
			for p in xrange(n):
				for r in xrange(2,qwr.ROLE_WEREWOLF+1):
					if random.randint(0,i*i+20) <= 20:
						Action.objects.create(day=i+1,player=players[p],role_id=r,target=players[randiff(n,[p])])
				for r in xrange(5):
					if random.randint(0,i*i+r*r+20) <= 20:
						Action.objects.create(day=i+1,player=players[p],role_id=-(qwr.PHASE_DAY+r),target=players[randiff(n,[p])])
			p = random.choice(xrange(n))
			Action.objects.create(day=i+1,player=players[p],role_id=-(qwr.PHASE_DAY+5),target=players[randiff(n,[p])])


if __name__ != '__main__':
	dq = dQS()
	db = dDB()
