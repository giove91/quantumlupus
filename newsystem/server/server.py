#!/usr/bin/env pypy

from sqlalchemy import *
import sys, random, time
import db_url, ruleset as qwr


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
			if roles[i] > 0:
				break
		tot_states = num_permutation(roles,i)
		s = [-r for r in roles[:i]] + [r for r in roles[i:]]
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
#	DataBase					#
#################################

class DataBase:
	# init the database taken from a certain url
	def __init__(self,url,cont):
		self.actives = set()
		self.db = create_engine(url)
		self.md = MetaData(self.db)
		self.games	= Table('games',	self.md, autoload=True)
		self.players  = Table('players',  self.md, autoload=True)
		self.villages = Table('villages', self.md, autoload=True)
		self.status   = Table('status',   self.md, autoload=True)
		self.actions  = Table('actions',  self.md, autoload=True)
		self.logs	 = Table('logs',	 self.md, autoload=True)
		if not cont:
			self.games.delete().execute()
			self.villages.delete().execute()
			self.actions.delete().execute()
			self.players.update().execute(game_id=None)
		self.status.delete().execute()
		self.logs.delete().execute()
	# return the first game that is not already started
	def pop(self):
		for g in self.games.select().execute().fetchall():
			if g[0] not in self.actives:
				self.actives.add(g[0])
				return Village(self,g[0])
		return None
	# discard a game that is ended
	def drop(self,id):
		self.actives.discard(id)
		self.games.delete(self.games.c.id==id).execute()
		self.villages.delete(self.villages.c.game_id==id).execute()
		for p in self.players.select(self.players.c.game_id==id).execute().fetchall():
			self.status.delete(self.status.c.player_id==p[0]).execute()
			self.actions.delete(self.actions.c.player_id==p[0]).execute()
			self.logs.delete(self.logs.c.player_id==p[0]).execute()
		self.players.update(self.players.c.game_id==id).execute(game_id=None)
	# return the player name given the id
	def name(self,id):
		return self.players.select(self.players.c.id==id).execute().fetchall()[0][1]


#################################
#	Village						#
#################################

class Village:
	# init the village with a certain id and database
	def __init__(self,db,id):
		self.db = db
		self.id = id
		self.phase = 1
		self.state = None
		self.roles = []
		self.players = []
		self.countdown = None
		self.ballot = []
		self.name = db.games.select(db.games.c.id==id).execute().fetchall()[0][1]
		self.limit_day = db.games.select(db.games.c.id==id).execute().fetchall()[0][7]
		self.limit_night = db.games.select(db.games.c.id==id).execute().fetchall()[0][8]
		self.tie_draw = db.games.select(db.games.c.id==id).execute().fetchall()[0][11]
		self.tie_play_off = db.games.select(db.games.c.id==id).execute().fetchall()[0][12]
		self.tie_conclave = db.games.select(db.games.c.id==id).execute().fetchall()[0][13]
		self.seed = db.games.select(db.games.c.id==id).execute().fetchall()[0][14]
		if self.seed == 0:
			self.seed = int(time.time()) % 1000000
		db.games.update(db.games.c.id==id).execute(seed=self.seed)
		random.seed(self.seed)
		self.rseed = random.getstate()
	# the village is updated
	def __call__(self):
		if self.state == None:
			if self.read_roles():
				random.setstate(self.rseed)
				if self.limit_day is not None and self.limit_night is not None:
					self.countdown = int(time.time()) + self.limit_day + self.limit_night
					self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
				else:
					self.countdown = int(time.time()) + 1000000
				self.db.games.update(self.db.games.c.id==self.id).execute(day=1)
				self.db.games.update(self.db.games.c.id==self.id).execute(phase=qwr.PHASE_NIGHT)
				max_states = self.db.games.select(self.db.games.c.id==self.id).execute().fetchall()[0][10]
				self.state = QuantumState(self.roles,max_states)
				for i in xrange(len(self.players)):
					for j in xrange(qwr.ROLE_WEREWOLF+2):
						self.db.status.insert().execute(player_id=self.players[i],status_type=qwr.STATUS_ROLE,value_id=j,probability=0)
					for j in xrange(len(self.players)):
						self.db.status.insert().execute(player_id=self.players[i],status_type=qwr.STATUS_WOLFRIEND,value_id=self.players[j],probability=0)
					self.db.status.insert().execute(player_id=self.players[i],status_type=qwr.STATUS_DEATHDAY,value_id=0,probability=0)
				self.write_status()
				self.rseed = random.getstate()
			else:
				return False
		if self.db.games.select(self.db.games.c.id==self.id).execute().fetchall()[0][3] < 0:
			return True
		if self.end_game():
			return time.time() > self.countdown
		a = [[None for j in xrange(qwr.ROLE_WEREWOLF+1)] for i in xrange(len(self.players))]
		if not self.read_actions(a) and time.time() < self.countdown:
			return False
		if self.phase == qwr.PHASE_DAY:
			random.setstate(self.rseed)
			if not self.lynch(a):
				self.db.actions.delete(self.db.actions.c.day==self.state.day)
				if self.limit_day is not None:
					self.countdown = int(time.time()) + self.limit_day
					self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
				else:
					self.countdown = int(time.time()) + 1000000
				return False
			self.phase = qwr.PHASE_NIGHT
			self.db.games.update(self.db.games.c.id==self.id).execute(phase=qwr.PHASE_NIGHT)
			if self.limit_night is not None:
				self.countdown = int(time.time()) + self.limit_night
				self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
			else:
				self.countdown = int(time.time()) + 1000000
			self.rseed = random.getstate()
			return False
		if self.phase == qwr.PHASE_NIGHT:
			random.setstate(self.rseed)
			self.apply(a)
			self.state += 1
			self.phase = qwr.PHASE_DAY
			self.db.games.update(self.db.games.c.id==self.id).execute(day=self.state.day)
			self.db.games.update(self.db.games.c.id==self.id).execute(phase=qwr.PHASE_DAY)
			if self.limit_day is not None:
				self.countdown = int(time.time()) + self.limit_day
				self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
			else:
				self.countdown = int(time.time()) + 1000000
			self.rseed = random.getstate()
			return False
	# read roles present and players subscribed, and check weather there are all of them
	def read_roles(self):
		self.players = [i[0] for i in self.db.players.select(self.db.players.c.game_id==self.id).execute().fetchall()]
		self.roles = [[i[1]*(1 if i[2] else -1) for j in xrange(i[3])] for i in self.db.villages.select(self.db.villages.c.game_id==self.id).execute().fetchall()]
		self.roles = sum(self.roles,[])
		max_players = self.db.games.select(self.db.games.c.id==self.id).execute().fetchall()[0][9]
		if len(self.roles) < len(self.players) and len(self.roles) < self.max_players:
			self.players = []
			self.roles = []
			return False
		if len(self.players) > max_players:
			for p in self.players[max_players:]:
				self.db.players.update(self.db.players.c.id==p).execute(game_id=None)
			self.players = self.players[:max_players]
		if len(self.roles) > len(self.players):
			self.roles = self.roles[:len(self.players)]
		return True
	# read the actions of the corresponding day and village, returns false if people missing
	def read_actions(self, actions):
		d = {}
		for p in xrange(len(self.players)):
			d[self.players[p]] = p
		done = True
		for p in self.players:
			for i in self.db.actions.select().where(self.db.actions.c.day==self.state.day).where(self.db.actions.c.player_id==p).execute().fetchall():
				actions[d[p]][i[3]] = d[i[4]]
			for i in xrange(qwr.ROLE_WEREWOLF+1):
				if qwr.ROLE_DESC[i][1] in [qwr.ROLE_MEASURE, qwr.ROLE_TRANSFORM] and actions[d[p]][i] is None and self.state[d[p]][qwr.STATUS_ROLE][i] > 0:
					done = False
		return done
	# write the status of the village in table "status"
	def write_status(self):
		for i in xrange(len(self.players)):
			for j in xrange(qwr.ROLE_WEREWOLF+2):
				self.db.status.update().where(self.db.status.c.player_id==self.players[i]).where(self.db.status.c.status_type==qwr.STATUS_ROLE).where(self.db.status.c.value_id==j).execute(probability=self.state[i][qwr.STATUS_ROLE][j]/float(len(self.state)))
			for j in xrange(len(self.players)):
				self.db.status.update().where(self.db.status.c.player_id==self.players[i]).where(self.db.status.c.status_type==qwr.STATUS_WOLFRIEND).where(self.db.status.c.value_id==self.players[j]).execute(probability=self.state[i][qwr.STATUS_WOLFRIEND][j]/float(len(self.state)))
			self.db.status.update().where(self.db.status.c.player_id==self.players[i]).where(self.db.status.c.status_type==qwr.STATUS_DEATHDAY).execute(probability=self.state[i][qwr.STATUS_DEATHDAY]/float(len(self.state)))
	# check the pool, lynch the winner and return false if tied
	def lynch(self, votes):
		res = [[1] for i in votes]
		for v in xrange(len(votes)):
			# solo in questo caso il voto e' valido
			if votes[v][1] is not None and (self.ballot == [] or votes[v][1] in self.ballot) and self.state[v][qwr.STATUS_ROLE][qwr.ROLE_DEAD] < len(self.state) and self.state[votes[v][1]][qwr.STATUS_ROLE][qwr.ROLE_DEAD] < len(self.state):
				res[votes[v][1]] += [v]
				res[votes[v][1]][0] += 1
		txt = [[res[i][0]-1,i] for i in xrange(len(res))]
		txt.sort()
		txt = '#'.join(['%s:\t%d (%s)' % (self.db.name(self.players[v[1]]),v[0],', '.join([self.db.name(self.players[i]) for i in res[v[1]][1:]])) for v in txt])
		win = [i for i in xrange(len(res)) if len(res[i]) == max(res)[0]]
		if len(win) > 1 and (self.tie_conclave or (self.tie_play_off and self.ballot == [])):
			if self.tie_play_off:
				self.ballot = win
			txt = "self.phrases[self.PHRASE_BALLOT] + '#" + txt + "'"
			self.db.logs.insert().execute(day=self.state.day,player_id=-self.id,content=txt)
			return False
		if len(win) == 1 or self.tie_draw:
			win = random.choice(win)
			self.state.lynch(win)
			txt = "self.phrases[self.PHRASE_LYNCH] %% '%s' + '#" % self.db.name(self.players[win]) + txt + "'"
		else:
			txt = "self.phrases[self.PHRASE_NOLYNCH] + '#" + txt + "'"
		self.db.logs.insert().execute(day=self.state.day,player_id=-self.id,content=txt)
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
					txt = "self.phrases[self.PHRASE_ACTION] %% (self.actions[%d], '%s')" % (i[1], self.db.name(self.players[i[2]]))
					if isinstance(res,bool):
						txt += ' + self.phrases[self.PHRASE_TRUE]' if res else ' + self.phrases[self.PHRASE_FALSE]'
					elif isinstance(res,int):
						txt += " + self.phrases[self.PHRASE_ID] %% '%s'" % self.db.name(self.players[res])
					txt += " + '.'"
					self.db.logs.insert().execute(day=self.state.day,player_id=self.players[i[0]],content=txt)
	# return wether the game is finished
	def end_game(self):
		return self.state.winner() is not None


#################################
#	Main						#
#################################


if __name__ == '__main__':
	db = DataBase(db_url.url, len(sys.argv) > 1 and sys.argv[1] == '-c')
	villages = []
	while True:
		villages += [db.pop()]
		if villages[-1] == None:
			villages.pop()
		for v in villages:
			if v():
				db.drop(v.id)
				villages.remove(v)


#################################
#	Debug						#
#################################


if __name__ != '__main__':
	import localization as qwl


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
		d = qwl.it
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
		self.names = ['Ammalia','Brumo','Carna','Darlo','Elica','Fascio','Gorgo','Hanno','Iene','Lucca','Marcio','Nicolla','Orario','Pallo','Quisto','Rodeo','Sana','Tiziamo','Uggio','Vanesio','Zorro']


class dDB:
	def __init__(self):
		self.db = DataBase(db_url.url, False)
	def __iadd__(self,n):
		for i in xrange(n):
			self.db.players.insert().execute(name=self.randname(i),mail=(self.randstr()+'.'+self.randstr()+'@'+self.randstr()+'.com'),password=self.randstr())
		return self
	def __call__(self):
		d = qwl.it
		villages = []
		while True:
			villages += [self.db.pop()]
			if villages[-1] == None:
				villages.pop()
			for v in villages:
				if (v.state is not None):
					print "\n===============================\nVillaggio %s" % v.name
					print "--- %s %d ---" % ('giorno' if v.phase == qwr.PHASE_DAY else 'notte', v.state.day)
					self.display(v)
				if v():
					print "\nHANNO VINTO I %s!\n" % ('VILLICI' if v.state.winner() else 'LUPI')
					print "--- final day ---"
					self.display(v)
					self.db.drop(v.id)
					villages.remove(v)
				if v.phase == qwr.PHASE_DAY and v.state is not None:
					if v.state.day == 1:
						print "\n===============================\nVillaggio %s" % v.name
						print "--- %s %d ---" % ('giorno' if v.phase == qwr.PHASE_DAY else 'notte', v.state.day)
						self.display(v)
					for i in self.db.logs.select(self.db.logs.c.day==v.state.day-1).execute().fetchall():
						if i[2] in v.players:
							print "[%s] %s" % (self.db.name(i[2]), d(i[3]))
				elif v.state is not None:
					for i in self.db.logs.select(self.db.logs.c.day==v.state.day).execute().fetchall():
						if i[2] == -v.id:
							print "[Day %d]" % v.state.day, '\n'.join(d(i[3]).split('#'))
	def display(self,vill):
		i = -3
		for l in repr(vill.state).split('\n'):
			f = l
			if i == -1:
				f = '\t' + f + '\t\t' + '\t'.join([self.db.name(vill.players[j]).split(' ')[0] for j in range(vill.state.N)])
			if i >= 0:
				f = self.db.name(vill.players[i]).split(' ')[0] + '\t' + f
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
		players = [int(i[0]) for i in self.db.players.select(self.db.players.c.game_id==None).execute().fetchall()]
		if len(players) > n:
			players = random.sample(players,n)
		else:
			n = len(players)
			roles = roles[:n]
		players.sort()
		gid = random.choice(players)
		self.db.games.insert().execute(name=self.randgame(),password=self.randstr(),admin_id=gid,limit_day=0,limit_night=0,max_players=n,max_states=100000,tie_draw=random.choice([True,False]),tie_play_off=random.choice([True,False]),tie_conclave=random.choice([True,False]))
		gid = self.db.games.select(self.db.games.c.admin_id==gid).execute().fetchall()[0][0]
		for i in players:
			self.db.players.update(self.db.players.c.id==i).execute(game_id=gid)
		for i in roles:
			self.db.villages.insert().execute(game_id=gid,role_id=abs(i),is_quantum=i<0)
		for i in xrange(20):
			for p in xrange(n):
				for r in xrange(1,qwr.ROLE_WEREWOLF+1):
					if random.randint(0,i*i+20) <= 20:
						self.db.actions.insert().execute(day=i+1,player_id=players[p],role_id=r,target_id=players[randiff(n,[p])])
	def randgame(self):
		return random.choice(['Col','Pra','Pian','Mon','Stra','Val']) + ''.join(random.choice(['pantan','sec','stort','salic','bel','mal','sul','viv','sol','lun','chiar','scur','fluvi','ari','os','buon','de','di','le','la','tra','fra','con']) for i in xrange(random.randint(2,4)/2)) + random.choice('aeioo')
	def randstr(self):
		return ''.join(''.join(random.choice('bccddfglllmnnnprrrsstttv') for j in xrange(random.randint(1,4)/2))+random.choice('aaaaeeeeiiiioou') for i in xrange(random.randint(2,6)))
	def randname(self,i):
		names = ['Ammalia','Brumo','Carna','Darlo','Elica','Fascio','Gorgo','Hanno','Iene','Lucca','Marcio','Nicolla','Orario','Pallo','Quisto','Rodeo','Sana','Tiziamo','Uggio','Vanesio','Zorro']
		name = self.randstr()
		return names[i] + ' ' + name[0].upper() + name[1:]


if __name__ != '__main__':
	dq = dQS()
	db = dDB()
