#!/usr/bin/env pypy

import ruleset as qwr
import re, random


class Dictionary:
	def __init__(self, phase, role, action, phrase):
		self.PHRASE_LYNCH	= 0
		self.PHRASE_BALLOT	= 1
		self.PHRASE_NOLYNCH	= 2
		self.PHRASE_ACTION	= 3
		self.PHRASE_TRUE	= 4
		self.PHRASE_FALSE	= 5
		self.PHRASE_ID		= 6
		self.PHRASE_VILLAGE = 7
		self.phases = phase
		self.roles = role
		self.actions = action
		self.phrases = phrase
		self.greek = ['Alfa', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mi', 'Ni', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Ypsilon', 'Phi', 'Chi', 'Psi', 'Omega']
	def __call__(self,txt,aslist=False):
		try:
			txt = eval('"' + re.sub('<([A-Z][A-Z]*):? *([^>]*)>','" + self.phrases[self.PHRASE_\\1] % (\\2) + "',re.sub('([a-z]*[a-z])\[([0-9][0-9]*)\]','" + self.\\1(\\2) + "',txt)) + '"').split('|')
			if not aslist:
				txt = '\n'.join(txt)
			return txt
		except:
			a = '"' + re.sub('<([A-Z][A-Z]*):? *([^>]*)>','" + self.phrases[self.PHRASE_\\1] % (\\2) + "',re.sub('([a-z]*[a-z])\[([0-9][0-9]*)\]','" + self.\\1(\\2) + "',txt)) + '"'
			return [txt + '||' + a]
	def phase(self,i):
		return self.phases[0 if i == qwr.PHASE_DAY else 1]
	def role(self,i):
		return self.roles[i]
	def finalrole(self,i):
		if i < qwr.ROLE_WEREWOLF:
			return self.roles[i]
		else:
			return self.roles[-1] % self.greek[i-qwr.ROLE_WEREWOLF]
	def action(self,i):
		return self.actions[i].split('|')[0]
	def acted(self,i):
		if len(self.actions[i].split('|')) == 1:
			return re.sub(self.actions[-2],self.actions[-1],self.actions[i].lower())
		else:
			return self.actions[i].split('|')[1]

default = 'it'
dict_list = {}
dict_list['it'] = Dictionary(['Giorno','Notte'], ['Morto','Contadino','Veggente','Medico','Stalker','Custode','Prete','Rianimatore','Sciamano','Cacciatore','Guardia','Sindaco','Amante','Lupo','Lupo dominante','Lupo %s'], ['Infesta','Coltiva','Scruta','Visita','Pedina','Custodisci|custodito','Benedici|benedetto','Rianima','Reincarna','Caccia','Proteggi|protetto','Sindaca','Ama','Morsica','$','to'], ['%s \xc3\xa8 stato linciato!||Voti:|====', 'Nessuno \xc3\xa8 stato linciato, la votazione prosegue!||Voti:|====', 'Nessuno \xc3\xa8 stato linciato!||Voti:|====', 'Hai %s %s', ' con esito positivo', ' con esito negativo', ' scoprendo %s','Villaggio %s'])

dict_list['en'] = Dictionary(['Day','Night'], ['Dead','Commoner','Seer','Physician','Stalker','Watchman','Priest','Reviver','Shaman','Hunter','Guard','Mayor','Lover','Werewolf','Dominant werewolf','%s werewolf'], ['Infest','Cultivate','Seer','Examine','Stalk','Watch','Bless','Revive','Reincarnate','Hunt','Guard','Mayor','Love','Bite|bitten','e?$','ed'], ['%s has been lynched!||Votes:|====', 'Nobody has been lynched, votation continues!||Votes:|====', 'Nobody has been lynched!||Votes:|====', 'You have %s %s', ' positively', ' negatively', ' finding %s','Village %s'])

def lang(key=None):
	if key is None:
		return dict_list.keys()
	if key in dict_list:
		return dict_list[key]
	return dict_list[default]

def randgame():
	return re.sub('([aeiou])\\1*','\\1', random.choice(['Col','Pra','Pian','Mon','Stra','Val']) + ''.join(random.choice(['pantan','sec','stort','salic','bel','mal','sul','viv','sol','lun','chiar','scur','fluvi','ari','os','buon','de','di','le','la','tra','fra','con']) for i in xrange(random.randint(2,4)/2)) + random.choice('aeioo'))

def randstr():
	return ''.join(''.join(random.choice('bccddfglllmnnnprrrsstttv') for j in xrange(random.randint(1,4)/2))+random.choice('aaaaeeeeiiiioou') for i in xrange(random.randint(2,6)))

def randname():
	name = randstr()
	return random.choice(['Ammalia','Brumo','Carna','Darlo','Elica','Fascio','Gorgo','Hanno','Iene','Lucca','Marcio','Nicolla','Orario','Pallo','Quisto','Rodeo','Sana','Tiziamo','Uggio','Vanesio','Zorro']) + ' ' + name[0].upper() + name[1:]
