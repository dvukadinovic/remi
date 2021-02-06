import random

class Card(object):
	def __init__(self, value, symbol):
		self.value = value
		self.symbol = symbol
		self.img = None
		self.for_trash = False
		self.active = False

	def __str__(self):
		return "<value: {:2d}; symbol: {:}>".format(self.value,self.symbol)

	def __eq__(self, x):
		if not isinstance(x, Card):
			return NotImplemented
		return x.value==self.value and x.symbol==self.symbol

	def get_value(self):
		return self.value

	def get_symbol(self):
		return self.symbol

class Deck(object):
	def __init__(self, num=1, njoker=None):
		"""
		Initialize the deck.

		Parameters:
		-----------
		num : (int)
			number of decks to initialize (default 1 == 52 cards).
		njoker : (int)
			how many jokers to initialize (default None).
		"""
		self.cards = []
		for _ in range(num):
			for symb in ["d","h","c","s"]:
				for number in range(1,15):
					if number==11:
						pass
					else:
						if number>=12:
							val = 10
						else:
							val = number
						self.cards.append(Card(val,f"{number}{symb}"))
	
		if njoker:
			for _ in range(njoker):
				self.cards.append(Card(0,"joker"))
		self.size = len(self.cards)

	def get_card(self,id):
		return self.cards[id]

	def shuffle(self):
		for _ in range(7):
			random.seed()
			random.shuffle(self.cards)

class Player(object):
	def __init__(self, name, pID):
		self.name = name
		self.ID = pID
		#--- points in game
		self.points = 0
		#--- list of Cards in Players hand
		self.cards = None
		#--- flag for Player opening his cards when he took the 'trash' card
		self.to_open = False
		#--- flag which is True when Player took the 'hand' card
		self.hand_end = False
		#--- flag which holds if Player have opened his cards
		self.opened = False
		#--- number of points in opening phase of game
		self.opening_points = 0
		#--- flag for updating window
		self.game_update_win = True
		#--- flag for new card
		self.got_new_card = False

class Game(object):
	"""
	Remi game object. Number of decks is always 2.
	"""
	def __init__(self, np, njoker=None):
		self.deck = Deck(num=2, njoker=njoker)
		self.np = np
		self.players = [None]*self.np
		#--- who of the players is taking the move
		self.moved = [True]*self.np
		#--- number of joined users to the game
		self.ID_counter = -1
		#--- flag which states if we should deal cards; deal when all players have connected
		self.deal_flag = False
		#--- game is ready?
		self.ready = False
		#--- flag for pauseing game
		self.pause = False
		#--- reset game flag (for each player)
		self.reset = [None]*self.np
		#--- current circle number
		self.circle = 1
		#--- current game round
		self.round = 1
		#--- hand card
		self.hand = None
		#--- thrown cards from the play
		self.trash = []
		#--- board cards
		self.board = []

	def deal(self):
		"""
		moramo da proverimo da li nema 3x duple karte. ako da, onda delimo ponovo

		uvesti brojac koji vodi racuna ko je na potezu u igri (svaka nova partija
		znaci da naredni igrac krece).

		podeli razlicite segmente u funkcije

		"""
		n = self.deck.size
		self.free_cards = list(range(n))

		#--- initial card on the table (za 'hand')
		while True:
			ind = random.randint(0,n-1)
			self.hand = self.deck.cards[ind]
			if self.hand.symbol=="joker":
				self.players[0].cards = [self.hand]
				got_joker = True
			else:
				got_joker = False
				break
			self.free_cards.remove(ind)

		#--- deal the cards to the players
		for j in range(self.np):
			if j==0:
				if got_joker:
					inds = random.sample(self.free_cards, 14)
					for i in inds:
						self.players[j].cards.append(self.deck.cards[i])
						self.free_cards.remove(i)
				else:
					inds = random.sample(self.free_cards, 15)
					self.players[j].cards = [self.deck.cards[i] for i in inds]
				for i in inds:
					self.free_cards.remove(i)
			else:
				inds = random.sample(self.free_cards, 14)
				self.players[j].cards = [self.deck.cards[i] for i in inds]
				for i in inds:
					self.free_cards.remove(i)
			# self.sort_cards_in_hand(j)

		self.deal_flag = False
		#--- first player is on the move
		self.moved[0] = False
		self.players[0].got_new_card = True
		#--- game is ready for play
		self.ready = True

	def sort_cards_in_hand(self, pID):
		"""
		Sort cards in hand.

		Lowest numbers are on the left, highest on the right (joker is on the right).
		"""
		cards = self.players[pID].cards
		has_joker = False
		num = 0
		for card in cards:
			if card.symbol=="joker":
				cards.remove(card)
				has_joker = True
				num += 1

		cards = sorted(cards, key=lambda x: int(x.symbol[:-1]))
		if has_joker:
			for i_ in range(num):
				cards.append(Card(0,"joker"))

		self.players[pID].cards = cards
		
	def add_player(self, pname):
		"""
		Add players in the game and return their ID. If the game is full return
		"full".

		When all the players are in the game, deal the cards and set 'ready' flag to
		True.
		"""
		self.ID_counter += 1
		if self.ID_counter>=self.np:
			return "full"
		else:
			self.players[self.ID_counter] = Player(pname, self.ID_counter)
			if self.ID_counter == self.np-1:
				self.deal_flag = True
				self.deal()
			return self.ID_counter

	def reset_game(self, pID, decision):
		"""
		u samoj igri se ne promeni hand karta i karte u 
		ruci igraca. Moram ponovo da loadujem slike (posto sam ih bio
		izbacio iz liste) i da odredim hand kartu i da nacrtam.

		Prakticno idemo ponovo u run_game() funkciju.
		"""
		#--- reset game
		self.reset[pID] = decision
		#--- check if all players are resetting
		if all(self.reset):
			# we are resetting the game:
			#   clear the score
			#   redeal the cards
			self.circle = 1
			self.deal()
			self.reset = [None]*self.np
			self.pause = False
			print("Game reseted!")
		else:
			if decision:
				self.pause = True
			else:
				self.pause = False
			br = 0
			for flag in self.reset:
				if flag!=None:
					br += 1
			if br==self.np:
				self.reset = [None]*self.np

	def made_move(self, pID, card):
		"""
		Switch flags after player finishes his move.

		Check if player has finished opening his cards. If not, retrurn him.
		"""
		self.moved[pID] = True
		self.players[pID].got_new_card = False
		self.check_game_end()
		if pID==self.np-1:
			self.moved[0] = False
			self.circle += 1
		else:
			self.moved[pID+1] = False
		self.trash.append(card)
		# sta ako ima dve karte u spilu koje su iste?
		for i_, c in enumerate(self.players[pID].cards):
			if c.value==card.value and c.symbol==card.symbol:
				ind = i_
				break
		self.players[pID].cards.pop(ind)
		self.update_players_win()

	def get_card_from_pile(self, pID):
		ind = random.choice(self.free_cards)
		self.players[pID].got_new_card = True
		self.free_cards.remove(ind)
		self.players[pID].cards.append(self.deck.cards[ind])
		self.players[pID].game_update_win = True

	def get_card_from_trash(self, pID):
		card = self.trash[-1]
		self.players[pID].cards.append(card)
		self.players[pID].got_new_card = True
		self.trash.remove(card)
		self.players[pID].to_open = True
		self.update_players_win()

	def get_card_for_hand(self, pID):
		self.players[pID].cards.append(self.hand)
		self.players[pID].hand_end = True
		self.players[pID].got_new_card = True
		self.hand = None
		self.update_players_win()

	def update_players_win(self):
		#--- set True flag for updating windows for all players
		for pID in range(self.np):
			self.players[pID].game_update_win = True

	def open_cards(self, pID, cards):
		# calculate points for given set of cards
		#--- remove cards from players hand
		for card in cards:
			self.players[pID].cards.remove(card)
		#--- add cards to board
		self.board.append(cards)
		#--- set to update players window
		self.update_players_win()

	def check_game_end(self):
		"""
		Check if the player ending his move has got rid of all the cards.

		Calculate players points.
		"""
		pass

if __name__=="__main__":
	game = Game(2, 8)
	p1 = game.add_player("Dusan")
	p2 = game.add_player("Debora")

	for_board = [Card(1,"1h"), Card(2,"2h"), Card(3,"3h"), Card(0,"joker")]

	# print(for_board)
	# check_card_set(for_board)
	# print(for_board)

	# flag = check_card_set(cards)
	# print(flag)