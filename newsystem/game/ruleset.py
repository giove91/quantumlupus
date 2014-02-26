#!/usr/bin/env pypy

import random

DAY_NONE		 = 0
PHASE_NIGHT		 = 1
PHASE_DAY		 = 2

ERROR_NEVER		 = 0
ERROR_TARGET	 = 1

STATUS_ROLE		 = 1
STATUS_WOLFRIEND = 2
STATUS_DEATHDAY	 = 3

PRIORITY_MAX	 = 6
RESULT_TRUE		 = 1024
DEATH_NULL		 = 1024

ROLE_NO			 = 0
ROLE_MEASURE	 = 1
ROLE_TRANSFORM	 = 2
ROLE_PASSIVE	 = 3

ROLE_DEAD		 = 0
ROLE_COMMONER	 = 1
ROLE_SEER		 = 2
ROLE_PHYSICIAN	 = 3
ROLE_STALKER	 = 4
ROLE_WATCHMAN	 = 5
ROLE_PRIEST		 = 6
ROLE_REVIVER	 = 7
ROLE_SHAMAN		 = 8
ROLE_HUNTER		 = 9
ROLE_GUARD		 = 10
ROLE_MAYOR		 = 11
ROLE_LOVER		 = 12
ROLE_WEREWOLF	 = 13
ROLE_WOLFMAX	 = ROLE_WEREWOLF + 24


def act_stalker(s,a,c,t,f):
	r = max(min(s[t][0], ROLE_WEREWOLF), 0)
	return a[t][r] if ROLE_DESC[r][1] in [ROLE_MEASURE, ROLE_TRANSFORM] else False

def act_watchman(s,a,c,t,f):
	if f is None:
		pool = [i for i in range(len(s)) if s[i][1] & ~DEATH_NULL == 0 and i != c and a[i][max(min(s[i][0], ROLE_WEREWOLF), 0)] == t]
		return random.choice(pool) if pool else False
	elif f is False:
		return bool([i for i in range(len(s)) if s[i][1] & ~DEATH_NULL == 0 and i != c and a[i][max(min(s[i][0], ROLE_WEREWOLF), 0)] == t])
	else:
		return f if s[f][1] & ~DEATH_NULL == 0 and a[f][max(min(s[f][0], ROLE_WEREWOLF), 0)] == t else False

def act_shaman(s,c,t,d):
	if s[t][1] & ~DEATH_NULL != 0:
		s[c][0] = -s[c][0]
		s[t][1] = 0

def act_hunter(s,c,t,d):
	if s[t][1] & ~DEATH_NULL == 0:
		s[c][0] = -s[c][0]
	if s[t][1] == 0:
		s[t][1] = d

def act_guard(s,c,t,d):
	if s[t][1] == 0:
		s[t][1] = DEATH_NULL

def act_mayor(s,c,t,d):
	if s[c][1] < 0:
		s[c][1] = 0

def act_lover(s,c,t,d):
	if s[c][1] & ~DEATH_NULL == 0 and [0 for i in s if i[0]==ROLE_LOVER and i[1] & ~DEATH_NULL != 0]:
		s[c][1] = d

def act_werewolf(s,c,t,d):
	if s[t][1] == 0 and s[t][0]<ROLE_WEREWOLF and not [0 for i in s if i[0]>=ROLE_WEREWOLF and i[0]<s[c][0] and i[1] & ~DEATH_NULL == 0]:
		s[t][1] = d


#							priority,	role type,	function,	error policy
ROLE_DESC				  = [[] for i in xrange(ROLE_WOLFMAX)]
ROLE_DESC[ROLE_DEAD]	  = [-1,ROLE_NO]
ROLE_DESC[ROLE_COMMONER]  = [-1,ROLE_NO]
ROLE_DESC[ROLE_SEER]	  = [1,	ROLE_MEASURE,	lambda s, a, c, t, f: s[t][0] < ROLE_WEREWOLF,					ERROR_TARGET]
ROLE_DESC[ROLE_PHYSICIAN] = [1,	ROLE_MEASURE,	lambda s, a, c, t, f: s[t][1] & ~DEATH_NULL == 0,				ERROR_TARGET]
ROLE_DESC[ROLE_STALKER]	  = [1,	ROLE_MEASURE,	act_stalker,													ERROR_NEVER]
ROLE_DESC[ROLE_WATCHMAN]  = [1,	ROLE_MEASURE,	act_watchman,													ERROR_NEVER]
ROLE_DESC[ROLE_PRIEST]	  = [0,	ROLE_MEASURE,	lambda s, a, c, t, f: s[t][0] < ROLE_WEREWOLF or f is None,		ERROR_TARGET]
ROLE_DESC[ROLE_REVIVER]	  = [0,	ROLE_MEASURE,	lambda s, a, c, t, f: s[t][1] & ~DEATH_NULL == 0 or f is None,	ERROR_TARGET]
ROLE_DESC[ROLE_SHAMAN]	  = [2,	ROLE_TRANSFORM,	act_shaman ]
ROLE_DESC[ROLE_HUNTER]	  = [4,	ROLE_TRANSFORM,	act_hunter ]
ROLE_DESC[ROLE_GUARD]	  = [3,	ROLE_TRANSFORM,	act_guard ]
ROLE_DESC[ROLE_MAYOR]	  = [-1,ROLE_PASSIVE,	act_mayor ]
ROLE_DESC[ROLE_LOVER]	  = [-1,ROLE_PASSIVE,	act_lover ]
for role in range(ROLE_WEREWOLF,ROLE_WOLFMAX):
	ROLE_DESC[role]		  = [5,	ROLE_TRANSFORM,	act_werewolf ]
