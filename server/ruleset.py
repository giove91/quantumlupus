#!/usr/bin/env pypy

import random

DAY_NONE		 = 0
PHASE_DAY		 = 1
PHASE_NIGHT		 = 2

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
ROLE_LOVER		 = 11
ROLE_WEREWOLF	 = 12
ROLE_WOLFMAX	 = ROLE_WEREWOLF + 24


def act_shaman(s,c,t,d):
	if s[t][1] != 0:
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

def act_lover(s,c,t,d):
	if [0 for i in s if i[0]==ROLE_LOVER and i[1] & ~DEATH_NULL != 0]:
		s[c][1] = d

def act_werewolf(s,c,t,d):
	if s[t][1] == 0 and not [0 for i in s if i[0]>=ROLE_WEREWOLF and i[0]<role and i[1] & ~DEATH_NULL == 0]:
		s[t][1] = d

#								priority,	type,	function,		optional: invalid return value
ROLE_DESC				  = [[] for i in xrange(ROLE_WOLFMAX)]
ROLE_DESC[ROLE_DEAD]	  = [0,	ROLE_NO]
ROLE_DESC[ROLE_COMMONER]  = [0,	ROLE_NO]
ROLE_DESC[ROLE_SEER]	  = [2,	ROLE_MEASURE,	lambda s, a, t, f: s[t][0] < ROLE_WEREWOLF]
ROLE_DESC[ROLE_PHYSICIAN] = [2,	ROLE_MEASURE,	lambda s, a, t, f: s[t][1] == 0]
ROLE_DESC[ROLE_STALKER]	  = [2,	ROLE_MEASURE,	lambda s, a, t, f: a[t][s[t]],													lambda c, t: [t]]
ROLE_DESC[ROLE_WATCHMAN]  = [2,	ROLE_MEASURE,	lambda s, a, t, f: random.choice([i for i in range(len(s)) if a[i][s[i]] == t]),lambda c, t: [c]]
ROLE_DESC[ROLE_PRIEST]	  = [1,	ROLE_MEASURE,	lambda s, a, t, f: s[t][0] < ROLE_WEREWOLF or not f]
ROLE_DESC[ROLE_REVIVER]	  = [1,	ROLE_MEASURE,	lambda s, a, t, f: s[t][1] == 0 or not f]
ROLE_DESC[ROLE_SHAMAN]	  = [3,	ROLE_TRANSFORM,	act_shaman ]
ROLE_DESC[ROLE_HUNTER]	  = [5,	ROLE_TRANSFORM,	act_hunter ]
ROLE_DESC[ROLE_GUARD]	  = [4,	ROLE_TRANSFORM,	act_guard ]
ROLE_DESC[ROLE_LOVER]	  = [7,	ROLE_PASSIVE,	act_lover ]
for role in range(ROLE_WEREWOLF,ROLE_WOLFMAX):
	ROLE_DESC[role]		  = [6,	ROLE_TRANSFORM,	act_werewolf ]
