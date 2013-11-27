#!/usr/bin/env python

from sqlalchemy import *
import dburl, sys

db = create_engine(dburl.giove)
db.echo = False

metadata = BoundMetaData(db)

time    = Table('ql_time',    metadata, autoload=True)
players = Table('ql_players', metadata, autoload=True)
waves   = Table('ql_waves',   metadata, autoload=True)
actions = Table('ql_actions', metadata, autoload=True)
roles   = Table('ql_roles',   metadata, autoload=True)

# ricostruisco la tabella ql_roles
roles.delete()
xri = roles.insert()
xri.execute(name='Morto')
xri.execute(name='Contadino')
xri.execute(name='Veggente')
xri.execute(name='Guardia')
xri.execute(name='Lupo')
# cancello la tabella time, come indicatore di "server not running"
time.delete()

if not (len(sys.argv) > 0 and sys.argv[0] == '-c'):
    # pulisco il resto del database
    players.delete()
    waves.delete()
    actions.delete()
    # chiedo come ricostruirlo
    print "Numero di giocatori: "
    N = int(sys.stdin.read())
    print "Numero di veggenti: "
    NV = int(sys.stdin.read())
    print "Numero di guardie: "
    NG = int(sys.stdin.read())
    print "Numero di lupi: "
    NL = int(sys.stdin.read())
    NC = N - NV - NG - NL
    xpi = players.insert()
    xwi = waves.insert()
    for i in range(N):
        print "Giocatore %d: " % i
        print "        nome: "
        nome = sys.stdin.read()
        print "    password: "
        pwd = sys.stdin.read()
        xpi.execute(name=nome, password=pwd, death=0)
        xwi.execute(player_id=i+1,role_id=1,0.0)
        xwi.execute(player_id=i+1,role_id=2,float(NC)/N)
        xwi.execute(player_id=i+1,role_id=3,float(NV)/N)
        xwi.execute(player_id=i+1,role_id=4,float(NG)/N)
        xwi.execute(player_id=i+1,role_id=5,float(NL)/N)

# SI PARTE!!!
xti = time.insert(day=1,phase=2)
xti.execute()

# cancello la tabella time, come indicatore di "server not running"
time.delete()
