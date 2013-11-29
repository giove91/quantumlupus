#!/usr/bin/env python

from sqlalchemy import *
import dburl, sys
import random


# giorno e stato sono variabili globali
day = 0
state = None
roles = [None,'Morto','Contadino','Veggente','Guardia','Lupo']


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


# classe che rappresenta uno stato quantistico
class QuantumState:
    def __len__(self):
        # restituisce il numero di stati rimasti
        return len(self.quantum)

    def __getitem__(self,i):
        # restituisce l'onda di probabilita' per i
        if self.waves is not None:
            return self.waves[i]
        self.waves[[0, 0, 0, 0, 0] for i in range(self.N)]
        for s in self.quantum():
            for j in range(self.N):
                self.waves[j][min(s[j][0],5)-1] += 1
                if s[j][1] > 0:
                    self.waves[j][0] += 1
        return self.waves[i]

    def lynch(self,kill):
        # lincia la persona kill
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

    def seer(self,cast target):
        # esegue uno scrutamento
        result = random.choice(list(self.quantum))[target][0] > 4
        nq = set()
        for s in self.quantum:
            if s[cast][0] != 3 or result == (s[target][0] > 4):
                nq.add(s)
        self.quantum = nq
        self.waves = None
        return result

    def bite(self,actions):
        # filtra per morsi e guardiamenti
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
            if state[bitten][0] < 5:
                ns = list(s)
                if bitten not in protected:
                    ns[bitten] = (ns[bitten][0],day)
                nq.add(tuple(ns))
        assert(len(nq)>0) #verificare l'asserzione
        self.quantum = nq
        self.waves = None

    def finished(self):
        # verifica se la partita e' finita, se si' restituisce lo stato
        deadwolves = 0
        goodliving = 0
        for i in range(self.N):
            if self[i][0] == self[i][4] == len(self):
                deadwolves += 1
            goodliving += max(len(self)-self[i][0]-self[i][4],0)
        if deadwolves == self.NL or goodliving == 0:
            # la partita e' finita.
            self.quantum=[random.choice(list(self.quantum))]
            return self.quantum
        return None

    def add(self,V,G,L):
        # aggiunge uno stato iniziale
        roles = [(2,0) for i in range(self.N)]
        for i in V:
            roles[i] = (3,0)
        for i in G:
            roles[i] = (4,0)
        for i in range(len(L)):
            roles[L[i]] = (5+i,0)
        self.quantum.add(tuple(roles))

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
# REM: death nella tabella: giorno medio di morte
class DataBase:
    def get_player_name(self,id):
        # guarda il nome nella tabella players
        return str(id)
    
    def initial_state(self):
        # restituisce lo stato iniziale
        return QuantumState(N,NV,NG,NL)
    
    def wait(self,phase):
        # aspetta che tutti facciano le loro azioni
        pass

    def get_actions(self):
        # restituisce le azioni inserite nel giorno di oggi
        pass

    def end_game(self):
        # logga le informazioni sul fine partita
        result = False
        for i in range(self.N):
            if state.quantum[0][i][0] > 4 and state.quantum[0][i][1] == 0:
                result = True
            logtext += '%s (%s)\n' % (get_player_name(i),role[state.quantum[0][i][0]])
        logtext = 'La partita e\' finita e hanno vinto i %s!\n Hanno giocato:\n' % ('lupi' if result else 'villici') + logtext
`       self.logs.insert().execute(0,day,logtext)

    def vote(self,votes):
        # esamina i voti, lincia e compila il log
        done = [False for i in range(self.N)]
        nvot = [[] for i in range(self.N)]
        for v in votes:
            if v[1] == 1 and not done[v[0]]:
                nvot[v[2]].append(v[0])
        winners = []
        maxv = max([len(i) for i in nvot])
        for i in range(self.N):
            if len(nvot[i]) == maxv:
                winners += i
        kill = choice(winners)
        logtext = 'Il giocatore %s e\' stato linciato, rivelandosi un %s.\r\n' % (get_player_name(kill), ('lupo' if state.lynch(kill) else 'villico'))
        for i in range(self.N):
            if len(nvot(i)) > 0:
                logtext += 'Voti per %s:\r\n' % get_player_name(i)
                for v in nvot(i):
                    logtext += '\t%s\r\n' % get_player_name(v)
                logtext += 'TOT: %d\r\n' % len(nvot(i))
        self.logs.insert().execute(0,day,logtext)

    def check_seerings(self,actions):
        # esegue in ordine casuale gli scrutamenti
        random.shuffle(actions)
        done = [False for i in range(self.N)]
        for a in actions:
            if a[1] == 3 and not done[a[0]]:
                self.logs.insert().execute(a[0],day,'Hai scrutato %s ed e\' risultato un %s.' % (get_player_name(a[2]), ('lupo' if state.seer(a[0],a[2]) else 'villico')) )

    def clear():
        # pulisco il resto del database e chiedo come ricostruirlo
        self.players.delete()
        self.waves.delete()
        self.actions.delete()
        self.logs.delete()
        print "Numero di giocatori: "
        N = int(sys.stdin.read())
        print "Numero di veggenti: "
        NV = int(sys.stdin.read())
        print "Numero di guardie: "
        NG = int(sys.stdin.read())
        print "Numero di lupi: "
        NL = int(sys.stdin.read())
        NC = N - NV - NG - NL
        xpi = self.players.insert()
        xwi = self.waves.insert()
        for i in range(N):
            print "Giocatore %d: " % i
            print "        nome: "
            nome = sys.stdin.read()
            print "    password: "
            pwd = sys.stdin.read()
            xpi.execute(name=nome, password=pwd, death=0)
            xwi.execute(player_id=i+1,role_id=1,probability=0.0)
            xwi.execute(player_id=i+1,role_id=2,probability=float(NC)/N)
        xwi.execute(player_id=i+1,role_id=3,probability=float(NV)/N)
        xwi.execute(player_id=i+1,role_id=4,probability=float(NG)/N)
        xwi.execute(player_id=i+1,role_id=5,probability=float(NL)/N)

    def __init__(self,url):
        # inizializzo il db
        self.db = create_engine(url)
        self.db.echo = False
        metadata = BoundMetaData(db)
        self.time    = Table('ql_time',    metadata, autoload=True)
        self.players = Table('ql_players', metadata, autoload=True)
        self.waves   = Table('ql_waves',   metadata, autoload=True)
        self.actions = Table('ql_actions', metadata, autoload=True)
        self.roles   = Table('ql_roles',   metadata, autoload=True)
        self.game    = Table('ql_game',    metadata, autoload=True)
        self.logs    = Table('ql_logs',    metadata, autoload=True)
        
        # ricostruisco la tabella ql_roles
        self.roles.delete()
        xri = self.roles.insert()
        for i in range(1,6):
            xri.execute(name=roles[i])
        # cancello la tabella time, come indicatore di "server not running"
        self.time.delete()


if __name__ == '__main__':
    db = DataBase(dburl.giove)
    if not (len(sys.argv) > 0 and sys.argv[0] == '-c'):
        db.clear()
    state = db.initial_state()

    for day in range(1,state.N):
        if day > 1:
            # giorno!
            #xti = time.insert(day=day,phase=1)
            #xti.execute()
            db.wait(True)
            db.vote(db.get_actions())
        # notte!
        #xti = time.insert(day=day,phase=2)
        #xti.execute()
        db.wait(False)
        a = db.get_actions()
        db.check_seerings(a)
        state.bite(a)
        if state.finished():
            db.end_game()
            break
