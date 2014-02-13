#!/usr/bin/env pypy


class Dictionary:
	def __init__(self, roles, actions, phrases):
		self.PHRASE_LYNCH	= 0
		self.PHRASE_BALLOT	= 1
		self.PHRASE_NOLYNCH	= 2
		self.PHRASE_ACTION	= 3
		self.PHRASE_TRUE	= 4
		self.PHRASE_FALSE	= 5
		self.PHRASE_ID		= 6
		self.roles = roles
		self.actions = actions
		self.phrases = phrases


it = Dictionary(['Morto','Contadino','Veggente','Medico','Stalker','Custode','Prete','Rianimatore','Sciamano','Cacciatore','Guardia','Sindaco','Amante','Lupo alfa','Lupo beta','Lupo gamma','Lupo delta','Lupo epsilon', 'Lupo zeta', 'Lupo eta', 'Lupo theta', 'Lupo iota', 'Lupo kappa', 'Lupo lambda', 'Lupo mi', 'Lupo ni', 'Lupo xi', 'Lupo omicron', 'Lupo pi', 'Lupo rho', 'Lupo sigma', 'Lupo tau', 'Lupo ypsilon', 'Lupo phi', 'Lupo chi', 'Lupo psi', 'Lupo omega'], ['infestato','coltivato','scrutato','visitato','pedinato','custodito','benedetto','rianimato','reincarnato','cacciato','protetto','sindacato','amato','morsicato'], ['%s \xc3\xa8 stato linciato!\n\nVoti:\n====', 'Nessuno \xc3\xa8 stato linciato, la votazione prosegue!\n\nVoti:\n====', 'Nessuno \xc3\xa8 stato linciato!\n\nVoti:\n====', '%s ha %s %s', ' con esito positivo', ' con esito negativo', ' scoprendo %s'])

en = Dictionary(['Dead','Commoner','Seer','Physician','Stalker','Watchman','Priest','Reviver','Shaman','Hunter','Guard','Mayor','Lover','Alfa werewolf','Beta werewolf','Gamma werewolf','Delta werewolf','Epsilon werewolf', 'Zeta werewolf', 'Eta werewolf', 'Theta werewolf', 'Iota werewolf', 'Kappa werewolf', 'Lambda werewolf', 'Mi werewolf', 'Ni werewolf', 'Xi werewolf', 'Omicron werewolf', 'Pi werewolf', 'Rho werewolf', 'Sigma werewolf', 'Tau werewolf', 'Ypsilon werewolf', 'Phi werewolf', 'Chi werewolf', 'Psi werewolf', 'Omega werewolf'], ['infested','cultivated','seered','examined','stalked','watched','blessed','revived','reincarnated','hunted','guarded','mayored','loved','bitten'], ['%s has been lynched!\n\nVotes:\n====', 'Nobody has been lynched, votation continues!\n\nVotes:\n====', 'Nobody has been lynched!\n\nVotes:\n====', '%s has %s %s', ' con esito positivo', ' con esito negativo', ' scoprendo %s'])
