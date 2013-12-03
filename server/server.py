#!/usr/bin/env pypy

from sqlalchemy import *
import sys, random, time
import db_url, localization as qwl, ruleset as qwr


###############################
#			utils			#
###############################

def randiff(N,v):
	if len(v) >= N or len(v) == 0:
		return random.randint(0,N-1)
	r = v[0]
	while r in v:
		r = random.randint(0,N-1)
	return r

###############################
#		permutations		 #
###############################

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


###############################
#		QuantumState		 #
###############################

class QuantumState:
	def __init__(self,roles, max_states):
		self.N = len(roles)
		self.quantum = []
		self.status = None
		self.end = False
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
	def __getitem__(self,id):
		if self.status is not None:
			return self.status[id]
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
					if not [0 for i in s if i[0]>=qwr.ROLE_WEREWOLF and i[0]<s[id][0] and i[1] & ~qwr.DEATH_NULL == 0]:
						self.status[id][qwr.STATUS_ROLE][qwr.ROLE_WEREWOLF+1] += 1
					for j in xrange(self.N):
						if s[j][0] >= qwr.ROLE_WEREWOLF:
							self.status[id][qwr.STATUS_WOLFRIEND][j] += 1
				else:
					self.status[id][qwr.STATUS_ROLE][abs(s[id][0])] += 1
		if wolf == False or good == False:
			self.end = True
		return self.status[id]
	def __repr__(self):
		s = '%d states' % len(self)
		for i in range(self.N):
			t = [str((10*self[i][qwr.STATUS_DEATHDAY]/self[i][qwr.STATUS_ROLE][qwr.ROLE_DEAD])/10.0) if self[i][qwr.STATUS_ROLE][qwr.ROLE_DEAD] > 0 else '0'] + [str(100*x/len(self))+'%' for x in self[i][qwr.STATUS_ROLE][:-1]]
			if self[i][qwr.STATUS_ROLE][-2] > 0:
				t += ['D:'+str(100*self[i][qwr.STATUS_ROLE][-1]/self[i][qwr.STATUS_ROLE][-2])+'%'] + [str(100*x/self[i][qwr.STATUS_ROLE][-2])+'%' for x in self[i][qwr.STATUS_WOLFRIEND]]
			s += '\n%s' % '\t'.join(t)
		return s
	def filter(self, check):
		j = 0
		for i in xrange(len(self)):
			if check(self.quantum(i)):
				self.quantum[j] = self.quantum[i]
				self.quantum[j]
				j += 1
		if j == 0:
			return False
		self.quantum = self.quantum[:j]
		return True
	def lynch(self, n, day):
		if not self.filter(lambda s: s[n][1] == 0):
			return False
		role = random.choice(self.quantum)[n][0]
		self.filter(lambda s: s[n][0] == role)
		for s in self.quantum:
			s[n][1] = -day
		self.status = None
		return True
	def measure(self, a, c, r, t, d):
		if qwr.ROLE_DESC[r][1] == qwr.ROLE_MEASURE:
			sample = random.choice(self.quantum)
			if sample[c][0] == r and sample[c][1] & ~qwr.DEATH_NULL == 0:
				res = qwr.ROLE_DESC[r][2](s,a,t,False)
			else:
				if len(qwr.ROLE_DESC[r] == 3):
					res = qwr.ROLE_DESC[r][2](s,a,randiff(self.N,c),False)
				else:
					res = randiff(self.N,qwr.ROLE_DESC[r][3])
			self.filter(lambda s: s[c][0] != r or s[c][1] & ~qwr.DEATH_NULL != 0 or (qwr.ROLE_DESC[r][2](s,a,t,True) == res))
			return res
		if qwr.ROLE_DESC[r][1] in (qwr.ROLE_TRANSFORM, qwr.ROLE_PASSIVE):
			for s in self.quantum:
				if s[c][0] == r and s[c][1] & ~qwr.DEATH_NULL == 0:
					qwr.ROLE_DESC[r][2](s,c,t,d)
		self.status = None
	def end_night(self):
		for s in self.quantum:
			for i in xrange(len(s)):
				if s[i][1] == qwr.DEATH_NULL:
					s[i][1] = 0
		self.status = None
	def winner(self):
		self.quantum = [random.choice(self.quantum)]
		imax = 0
		for id in xrange(1,self.N):
			if self.quantum[0][id][1] == 0:
				return self.quantum[0][id][0] < qwr.ROLE_WEREWOLF
			if self.quantum[0][id][1] < self.quantum[0][imax][1]:
				imax = id
		return (self.quantum[0][imax][0] < qwr.ROLE_WEREWOLF)


###############################
#		  DataBase		   #
###############################

class DataBase:
	# init the database taken from a certain url
	def __init__(self,url):
		self.actives = set()
		self.db = create_engine(url)
		self.md = MetaData(self.db)
		self.games	= Table('games',	self.md, autoload=True)
		self.players  = Table('players',  self.md, autoload=True)
		self.villages = Table('villages', self.md, autoload=True)
		self.status   = Table('status',   self.md, autoload=True)
		self.actions  = Table('actions',  self.md, autoload=True)
		self.logs	 = Table('logs',	 self.md, autoload=True)
		self.games.delete().execute()
		self.villages.delete().execute()
		self.status.delete().execute()
		self.actions.delete().execute()
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


###############################
#		   Village		   #
###############################

class Village:
	# init the village with a certain id and database
	def __init__(self,db,id):
		self.db = db
		self.id = id
		self.day = 1
		self.phase = qwr.PHASE_NIGHT
		self.state = None
		self.roles = []
		self.players = []
		self.countdown = None
		self.limit_day = db.games.select(db.games.c.id==id).execute().fetchall()[0][7]
		self.limit_night = db.games.select(db.games.c.id==id).execute().fetchall()[0][8]
		self.tie_draw = db.games.select(db.games.c.id==id).execute().fetchall()[0][11]
		self.tie_play_off = db.games.select(db.games.c.id==id).execute().fetchall()[0][12]
		self.tie_conclave = db.games.select(db.games.c.id==id).execute().fetchall()[0][13]
	# the village is updated
	def __call__(self):
		if self.state == None:
			if read_roles():
				if self.limit_day is not None and self.limit_night is not None:
					self.countdown = int(time.time()) + self.limit_day + self.limit_night
					self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
				else:
					self.countdown = int(time.time()) + 1000000
				self.db.games.update(self.db.games.c.id==self.id).execute(day=1)
				self.db.games.update(self.db.games.c.id==self.id).execute(phase=PHASE_NIGHT)
				max_states = self.db.games.select(self.db.games.c.id==self.id).execute().fetchall()[0][10]
				self.state = QuantumState(self.roles,max_states)
				self.write_status()
			return False
		a = None
		if time.time() < self.countdown and not read_actions(a):
			return False
		if self.phase == qwr.PHASE_DAY:
			self.lynch(a)
			self.phase = qwr.PHASE_NIGHT
			self.db.games.update(self.db.games.c.id==self.id).execute(phase=PHASE_NIGHT)
			if self.limit_night is not None:
				self.countdown = int(time.time()) + self.limit_night
				self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
			else:
				self.countdown = int(time.time()) + 1000000
			return self.end
		if self.phase == qwr.PHASE_NIGHT:
			self.measure(a)
			self.transform(a)
			self.day += 1
			self.phase = qwr.PHASE_DAY
			self.db.games.update(self.db.games.c.id==self.id).execute(day=self.day)
			self.db.games.update(self.db.games.c.id==self.id).execute(phase=PHASE_DAY)
			if self.limit_day is not None:
				self.countdown = int(time.time()) + self.limit_day
				self.db.games.update(self.db.games.c.id==self.id).execute(countdown=self.countdown)
			else:
				self.countdown = int(time.time()) + 1000000
			return self.end
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
	# read the actions of the corresponding day and village AAAAAAAAAAAAA
	def read_actions(self, actions):
		r = [None for i in self.players]
		done = True
		for p in self.players:
			t = self.db.actions.select().where(day==self.day).where(player_id==p).execute().fetchall()
			t = [i[3:] for i in t]
			r[p] = t
	# write the status of the village in table "status"
	def write_status(self):
		pass
	def lynch(self, votes):
		pass
	def measure(self, actions):
		pass
	def transform(self, actions):
		pass
	def end_game(self):
		return True


###############################
#			Debug			#
###############################


# classe che si interfaccia con il database
class DataBaseOld:
	def get_player_name(self,id):
		# guarda il nome nella tabella players
		return self.players.select(self.players.c.id==id+1).execute().fetchall()[0][1]

	def initial_state(self):
		# restituisce lo stato iniziale
		NC = self.game.select(self.game.c.role_id==2).execute().fetchall()[0][1]
		NV = self.game.select(self.game.c.role_id==3).execute().fetchall()[0][1]
		NG = self.game.select(self.game.c.role_id==4).execute().fetchall()[0][1]
		NL = self.game.select(self.game.c.role_id==5).execute().fetchall()[0][1]
		N = NC + NV + NG + NL
		return QuantumState(N,NV,NG,NL)
	
	def update_waves(self):
		# aggiorna la tabella waves e death di players
		for i in range(state.N):
			for j in range(1,6):
				p = state[i][j]/float(len(state))
				self.waves.update().where(self.waves.c.player_id==i+1).where(self.waves.c.role_id==j).execute(probability=p)
				self.players.update(self.players.c.id==i+1).execute(death=(0 if state[i][1] < len(state) else 10*state[i][0]/state[i][1]))

	def get_actions(self):
		# restituisce le azioni inserite nel giorno di oggi
		r = self.actions.select(self.actions.c.day==day).execute().fetchall()
		return reversed([[a[1]-1,a[2],a[3]-1] for a in r])

	def turn_done(self,phase):
		# controlla se tutti hanno fatto le loro azioni
		for i in range(state.N):
			if state[i][1] < len(state):
				if phase and len(self.actions.select().where(self.actions.c.player_id==i+1).where(self.actions.c.type==1).where(self.actions.c.day==day).execute().fetchall()) == 0:
					return False
				for j in range(1,4):
					if not phase and state[i][j+2] > 0 and len(self.actions.select().where(self.actions.c.player_id==i+1).where(self.actions.c.type==j%3+2).where(self.actions.c.day==day).execute().fetchall()) == 0:
						return False
		return True

	def end_game(self):
		# logga le informazioni sul fine partita
		result = False
		logtext = ''
		imax=False
		for i in range(state.N):
			if state.quantum[0][i][1] == 0:
				imax = True
				if state.quantum[0][i][0] > 4:
					result = True
		if not imax:
			imax=0
			for i in range(1,state.N):
				if state.quantum[0][i][1] > state.quantum[0][imax][1]:
					imax=i
			result = (state.quantum[0][imax][0] > 4)
		self.logs.insert().execute(player_id=0,day=day,content='La partita e\' finita e hanno vinto i %s!!  Hanno giocato:' % ('lupi' if result else 'villici'))
		for i in range(state.N):
			self.logs.insert().execute(player_id=0,day=day,content='%s (%s)' % (self.get_player_name(i),roles[state.quantum[0][i][0]]))

	def vote(self,votes):
		# esamina i voti, lincia e compila il log
		done = [False for i in range(state.N)]
		nvot = [[] for i in range(state.N)]
		for v in votes:
			if v[1] == 1 and not done[v[0]] and state[v[0]][1] < len(state) and state[v[2]][1] < len(state):
				nvot[v[2]].append(v[0])
				done[v[0]] = True
		winners = []
		maxv = max([len(i) for i in nvot])
		for i in range(state.N):
			if len(nvot[i]) == maxv:
				winners += [i]
		kill = random.choice(winners)
		self.logs.insert().execute(player_id=0,day=day,content='Il giocatore %s e\' stato linciato, rivelandosi un %s.' % (self.get_player_name(kill), ('lupo' if state.lynch(kill) else 'villico')))
		for i in range(state.N):
			if len(nvot[i]) > 0:
				logtext = 'Voti per %s  (TOT %d):  ' % (self.get_player_name(i),len(nvot[i]))
				for v in nvot[i]:
					logtext += ' %s' % self.get_player_name(v)
				self.logs.insert().execute(player_id=0,day=day,content=logtext)

	def check_seerings(self,actions):
		# esegue in ordine casuale gli scrutamenti
		random.shuffle(actions)
		done = [False for i in range(state.N)]
		for a in actions:
			if a[1] == 3 and not done[a[0]]:
				self.logs.insert().execute(player_id=a[0]+1,day=day,content='Hai scrutato %s ed e\' risultato un %s.' % (self.get_player_name(a[2]), ('lupo' if state.seer(a[0],a[2]) else 'villico')) )
				done[a[0]] = True

	def log_actions(self, actions):
		done = [[False,False] for i in range(state.N)]
		for a in actions:
			if (a[1] == 2 or a[1] == 4) and not done[a[0]][a[1]/2-1]:
				self.logs.insert().execute(player_id=a[0]+1,day=day,content='Hai %s %s.' % (('sbranato' if a[1] == 2 else 'protetto'), self.get_player_name(a[2])) )

	def clear(self):
		# pulisco il database e chiedo come ricostruirlo
		print "Attesa connessioni (premere invio per cominciare la partita)...",
		sys.stdin.readline()
		db.time.insert().execute(day=1,phase=1)
		N = len(self.players.select().execute().fetchall())
		print "Numero di veggenti: ",
		NV = int(sys.stdin.readline())
		print "Numero di guardie: ",
		NG = int(sys.stdin.readline())
		print "Numero di lupi: ",
		NL = int(sys.stdin.readline())
		print "Stati iniziali (vuoto per tutti gli stati)",
		k = sys.stdin.readline()[:-1]
		if k == '':
			k = 2.0
		else:
			k = eval(k)
		NC = N - NV - NG - NL
		self.game.insert().execute(role_id=2,num=NC)
		self.game.insert().execute(role_id=3,num=NV)
		self.game.insert().execute(role_id=4,num=NG)
		self.game.insert().execute(role_id=5,num=NL)
		for i in range(1,5):
			self.roles.insert().execute(id=i,name=roles[i])
		self.roles.insert().execute(id=5,name='Lupo')
		for i in range(N):
			for j in range(1,6):
				self.waves.insert().execute(player_id=i+1,role_id=j,probability=0.0)
		global state
		state = QuantumState(N,NV,NG,NL,k)
		self.update_waves()


if __name__ == '__main__' and False:
	db = DataBase(dburl.url)
	if not (len(sys.argv) > 1 and sys.argv[1] == '-c'):
		db.clear()
	else:
		db.logs.delete().execute()
		state = db.initial_state()

	for x in range(1,state.N):
		day = x
		if day > 1:
			# giorno!
			db.time.delete().execute()
			db.time.insert().execute(day=day,phase=1)
			counter = 0
			while not db.turn_done(True) and counter < 150:
				time.sleep(2)
				counter += 1
			a = db.get_actions()
			db.log_actions(a)
			db.vote(a)
			db.update_waves()
			if state.finished():
				db.end_game()
				db.update_waves()
				break
		print state
		# print state.quantum
		# notte!
		db.time.delete().execute()
		db.time.insert().execute(day=day,phase=2)
		counter = 0
		while not db.turn_done(False) and counter < 60:
			time.sleep(2)
			counter += 1
		a = db.get_actions()
		db.log_actions(a)
		db.check_seerings(a)
		state.bite(a)
		db.update_waves()
		if state.finished():
			db.end_game()
			db.update_waves()
			break
		print state
		# print state.quantum
	print state
	# print state.quantum
	names = ['Ammalia','Brumo','Carna','Darlo','Elica','Fascio','Gorgo','Hanno','Iene','Lucca','Marcio','Nicolla']

# logs.insert().execute(content='nuovo contenuto')
# logs.delete(logs.c.player_id==1).execute()
# logs.update(logs.c.player_id==2).execute(content='Nuovo contenuto')
# logs.select(logs.c.player_id==2).execute().fetchall()

class DEBUG():
	def randiff(self,N,i):
		r = i
		while r == i:
			r = random.randint(0,N-1)
		return r
	
	def randact(self,N):
		a = []
		for k in range(1,5):
			a += [[i,k,self.randiff(N,i)] for i in range(N)]
		return a
	
	def setup(self):
		global state
		global day
		day = 1
		state = QuantumState(10,1,1,2)
		print state
	
	def doday(self):
		global day
		assert(day>0)
		a = self.randact(state.N)
		DataBase.check_seerings(LOGS(),a)
		state.bite(a)
		print state
		if state.finished():
			return
		day = day+1
		DataBase.vote(LOGS(),a)
		print state
	
	def __call__(self):
		self.setup()
		while not state.finished():
			self.doday()
		DataBase.end_game(LOGS())

if __name__ != '__main__':
	d = DEBUG()
