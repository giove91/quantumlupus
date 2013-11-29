#!/usr/bin/env python

from sqlalchemy import *
import dburl, sys, random, time


# giorno e stato sono variabili globali
day = 0
state = None
roles = [None,'Morto','Contadino','Veggente','Guardia','Lupo alfa','Lupo beta','Lupo gamma','Lupo delta','Lupo epsilon']


# funzione che calcola il successivo di una sequenza
def next(N,V):
    for i in reversed(range(len(V))):
        V[i] += 1
        while V[i] < N and V[i] in V[0:i]:
            V[i] += 1
        if V[i] < N:
            for j in range(i+1,len(V)):
                V[j] = 0
                while V[j] in V[0:j]:
                    V[j] += 1
            return True
    return False


# DEBUG
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


# classe che rappresenta uno stato quantistico
class QuantumState:
    def __repr__(self):
        s = '%d \t(day %d)' % (len(self), day)
        for i in range(self.N):
            s += '\n%s' % '\t'.join([str((10*self[i][0]/self[i][1])/10.0) if self[i][1] > 0 else '0'] + [str(100*x/len(self))+'%' for x in self[i][1:]])
        return s
    
    def __len__(self):
        # restituisce il numero di stati rimasti
        return len(self.quantum)

    def __getitem__(self,i):
        # restituisce l'onda di probabilita' per i
        if self.waves is not None:
            return self.waves[i]
        self.waves = [[0, 0, 0, 0, 0, 0] for j in range(self.N)]
        for s in self.quantum:
            for j in range(self.N):
                self.waves[j][min(s[j][0],5)] += 1
                if s[j][1] > 0:
                    self.waves[j][1] += 1
                    self.waves[j][0] += s[j][1]
        return self.waves[i]

    def lynch(self,kill):
        # lincia la persona kill, che non deve essere gia' morta
        assert(self[kill][1] != len(self))
        nq = []
        for s in self.quantum:
            if s[kill][1] == 0:
                nq += [s]
        result = random.choice(nq)
        nq = set()
        for s in self.quantum:
            if s[kill] == result[kill]:
                ns = list(s)
                ns[kill] = (ns[kill][0],day)
                nq.add(tuple(ns))
        self.quantum = nq
        self.waves = None
        return result[kill][0] > 4

    def seer(self,cast,target):
        # esegue uno scrutamento
        result = random.choice(list(self.quantum))
        result = (result[target][0] if result[cast][0] == 3 else result[random.randint(0,self.N-1)][0] ) > 4
        nq = set()
        for s in self.quantum:
            if s[cast][0] != 3 or result == (s[target][0] > 4):
                nq.add(s)
        self.quantum = nq
        self.waves = None
        return result

    def bite(self,actions):
        # esegue morsi e guardiamenti
        nq = set()
        for s in self.quantum:
            alphawolf = -1
            for i in range(self.N):
                if s[i][0] > 4 and s[i][1] == 0 and (alphawolf == -1 or s[i][0] < s[alphawolf][0]):
                    alphawolf = i
            done = [False for i in range(self.N)]
            protected = []
            bitten = -1
            for a in actions:
                if a[1] == 2 and a[0] == alphawolf and bitten == -1:
                    bitten = a[2]
                if a[1] == 4 and s[a[0]] == (4,0) and not done[a[0]]:
                    protected += [a[2]]
                    done[a[1]] = True
            ns = list(s)
            if bitten >= 0 and bitten not in protected:
                ns[bitten] = (ns[bitten][0],day)
            nq.add(tuple(ns))
        self.quantum = nq
        self.waves = None

    def finished(self):
        # verifica se la partita e' finita, se si' restituisce lo stato
        deadwolves = 0
        goodliving = 0
        for i in range(self.N):
            if self[i][1] == self[i][5] == len(self):
                deadwolves += 1
            goodliving += max(len(self)-self[i][1]-self[i][5],0)
        if deadwolves == self.NL or goodliving == 0:
            # la partita e' finita.
            self.quantum = [random.choice(list(self.quantum))]
            self.waves = None
            return True
        return False

    def add(self,V,G,L):
        # aggiunge uno stato iniziale
        s = [(2,0) for i in range(self.N)]
        for i in V:
            s[i] = (3,0)
        for i in G:
            s[i] = (4,0)
        for i in range(len(L)):
            s[L[i]] = (5+i,0)
        self.quantum.add(tuple(s))

    def __init__(self,N,NV,NG,NL):
        # inizializzo con un certo numero di giocatori per ruolo
        self.N = N
        self.NL = NL
        self.quantum = set()
        self.waves = None
        V = [i for i in range(NV+NG+NL)]
        self.add(V[0:NV],V[NV:NV+NG],V[NV+NG:])
        while (next(N,V)):
            self.add(V[0:NV],V[NV:NV+NG],V[NV+NG:])


# classe che si interfaccia con il database
class DataBase:
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
                self.waves.update(self.waves.c.player_id==i,self.c.waves.role_id==j).execute(probability=state[i][j])
                self.players.update(self.players.c.id==i).execute(death=(0 if state[i][1] < len(state) else 10*state[i][0]/state[i][1]))

    def get_actions(self):
        # restituisce le azioni inserite nel giorno di oggi
        r = self.actions.select(self.actions.c.day==day).execute().fetchall()
        return [[a[1]-1,a[2],a[3]-1] for a in r]

    def turn_done(self,phase):
        # controlla se tutti hanno fatto le loro azioni
        for i in range(state.N):
            if state[i][1] < len(state):
                if phase and len(self.actions.select(self.actions.c.player_id==i+1,self.actions.c.type==1,self.actions.c.day==day).execute().fetchall()) == 0:
                    return False
                for j in range(1,4):
                    if not phase and state[i][j+2] > 0 and len(self.actions.select(self.actions.c.player_id==i+1,self.actions.c.type==j%3+2,self.actions.c.day==day).execute().fetchall()) == 0:
                        return False
        return True

    def end_game(self):
        # logga le informazioni sul fine partita
        result = False
        logtext = ''
        for i in range(state.N):
            if state.quantum[0][i][0] > 4 and state.quantum[0][i][1] == 0:
                result = True
        self.logs.insert().execute(player_id=0,day=day,content='La partita e\' finita e hanno vinto i %s!!  Hanno giocato:' % ('lupi' if result else 'villici'))
        for i in range(state.N):
            self.logs.insert().execute(player_id=0,day=day,content='%s (%s)' % (self.get_player_name(i),roles[state.quantum[0][i][0]]))

    def vote(self,votes):
        # esamina i voti, lincia e compila il log
        done = [False for i in range(state.N)]
        nvot = [[] for i in range(state.N)]
        for v in votes:
            if v[1] == 1 and not done[v[0]] and state[v[2]][1] < len(state):
                nvot[v[2]].append(v[0])
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
                self.logs.insert().execute(player_id=a[0],day=day,content='Hai scrutato %s ed e\' risultato un %s.' % (self.get_player_name(a[2]), ('lupo' if state.seer(a[0],a[2]) else 'villico')) )

    def clear():
        # pulisco il database e chiedo come ricostruirlo
        self.time.delete().execute()
        self.players.delete().execute()
        self.waves.delete().execute()
        self.actions.delete().execute()
        self.roles.delete().execute()
        self.game.delete().execute()
        self.logs.delete().execute()
        print "Numero di giocatori: "
        N = int(sys.stdin.read())
        print "Numero di veggenti: "
        NV = int(sys.stdin.read())
        print "Numero di guardie: "
        NG = int(sys.stdin.read())
        print "Numero di lupi: "
        NL = int(sys.stdin.read())
        NC = N - NV - NG - NL
        self.game.insert().execute(role_id=2,num=NC)
        self.game.insert().execute(role_id=3,num=NV)
        self.game.insert().execute(role_id=4,num=NG)
        self.game.insert().execute(role_id=5,num=NL)
        for i in range(1,5):
            self.roles.insert().execute(name=roles[i])
        self.roles.insert().execute(name='Lupo')
        for i in range(N):
            print "Giocatore %d: " % i
            print "        nome: "
            nome = sys.stdin.read()
            print "    password: "
            pwd = sys.stdin.read()
            self.players.insert().execute(name=nome, password=pwd, death=0)
        self.update_waves()

    def __init__(self,url):
        # inizializzo il db
        self.db = create_engine(url)
        self.md = MetaData(db)
        self.time    = Table('ql_time',    self.md, autoload=True)
        self.players = Table('ql_players', self.md, autoload=True)
        self.waves   = Table('ql_waves',   self.md, autoload=True)
        self.actions = Table('ql_actions', self.md, autoload=True)
        self.roles   = Table('ql_roles',   self.md, autoload=True)
        self.game    = Table('ql_game',    self.md, autoload=True)
        self.logs    = Table('ql_logs',    self.md, autoload=True)

# DEBUG
class LOGS(DataBase):
    def get_player_name(self,id):
        # guarda il nome nella tabella players
        return self.names[id]
    def insert(self):
        return self
    def execute(self,id,day,txt):
        print "LOG (day %d): %d -- %s" % (day, id, txt)
    def __init__(self):
        self.logs = self
        self.names = ['Ammalia','Brumo','Carna','Darlo','Elica','Fascio','Gorgo','Hanno','Iene','Lucca','Marcio','Nicolla']


if __name__ == '__main__':
    db = DataBase(dburl.local_giove)
    if not (len(sys.argv) > 0 and sys.argv[0] == '-c'):
        db.clear()
    else:
        db.logs.clear()
    state = db.initial_state()

    for x in range(1,state.N):
        day = x
        if day > 1:
            # giorno!
            db.time.delete().execute()
            db.time.insert().execute(day=day,phase=1)
            while not db.turn_done(True):
                time.sleep(2)
            db.vote(db.get_actions())
            if state.finished():
                db.end_game()
                break
        # notte!
        db.time.delete().execute()
        db.time.insert().execute(day=day,phase=2)
        while not db.turn_done(False):
            time.sleep(2)
        a = db.get_actions()
        db.check_seerings(a)
        state.bite(a)
        if state.finished():
            db.end_game()
            break

# logs.insert().execute(content='nuovo contenuto')
# logs.delete(logs.c.player_id==1).execute()
# logs.update(logs.c.player_id==2).execute(content='Nuovo contenuto')
# logs.select(logs.c.player_id==2).execute().fetchall()
