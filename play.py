import pygame
import gui
import glob
import game as Game

card_w, card_h = 100, 150
info_h = 80
side_width = 120

def load_imgs():
	img_list = glob.glob("resources/cards_100x150/*")
	imgs = {}
	for path in img_list:
		card_name = path.split("/")[2].rsplit(".")[0]
		imgs[card_name] = pygame.transform.scale(pygame.image.load(path), (card_w,card_h))

	return imgs

def draw_user_cards(win, cards):
	for card in cards:
		win.blit(card.img, (card.rect.x, card.rect.y))
		
def get_imgs_for_cards(cards, imgs, rect):
	x, y = 20, 20+rect.h
	dx = int((rect.w-card_w)/len(cards))
	for card in cards:
		card.img = imgs[card.symbol]
		card.rect = pygame.Rect(x, y, card_w, card_h)
		x += dx

def check_card_set(cards_for_check):
	#--- must have at least 3 cards
	cards = cards_for_check.copy()
	if len(cards)<3:
		return False

	#--- if there is joker in cards, remove it and flag it
	has_joker = False
	for card in cards:
		if card.symbol=="joker":
			cards.remove(card)
			has_joker = True
			break

	#--- sort cards by symbol
	cards = sorted(cards, key=lambda x: int(x.symbol[:-1]))

	value_flag = all(int(card.symbol[:-1])==int(cards[0].symbol[:-1]) for card in cards)
	symbol_flag = all(card.symbol[-1]==cards[0].symbol[-1] for card in cards)

	check = True
	#--- cards with same numbers
	if value_flag:
		for i_ in range(1,len(cards)):
			if cards[i_].symbol[-1]!=cards[i_-1].symbol[-1]:
				check = True and check
			else:
				check = False and check
		return check
	
	#--- cards with same symbol
	elif symbol_flag:
		for i_ in range(1,len(cards)):
			val1 = int(cards[i_].symbol[:-1])
			val2 = int(cards[i_-1].symbol[:-1])
			diff = val1 - val2
			if (abs(diff)==1) or \
			   (abs(diff)==2 and has_joker) or \
			   ((val1==10 and val2==12) or (val1==12 and val2==10)) or \
			   ((val1==10 and val2==13) or (val1==13 and val2==10) and has_joker) or \
			   ((val1==1 and val2==14) or (val1==14 and val2==1)) or \
			   ((val1==1 and val2==13) or (val1==13 and val2==1) and has_joker) or \
			   ((val1==9 and val2==13) or (val1==13 and val2==9) and has_joker):
				check = True and check
			else:
				check = False and check
		return check
	else:
		return False

def play(win,netw,pID):
	w, h = win.get_size()

	#--- define board
	board_w = w - side_width - 20*2
	board_h = h - info_h - 20*2 - card_h
	board_rect = pygame.Rect(20, 20, board_w, board_h)

	#--- define trash / hand / pile (aka 'side')
	side_w = side_width
	side_h = h - info_h
	side_rect = pygame.Rect(board_w, 0, side_w, side_h)

	gap_x = int((side_w-card_w)/2)
	gap_y = int((side_h-card_h*3)/4)

	# hand card rectangle
	hand_rect = pygame.Rect(board_w+gap_x, gap_y, card_w, card_h)

	# trash cards rectangle
	trash_rect = pygame.Rect(board_w+gap_x, card_h + 2*gap_y, card_w, card_h)

	# pile cards rectangle
	pile_rect = pygame.Rect(board_w+gap_x, card_h*2 + 3*gap_y, card_w, card_h)

	#--- define info / button
	block_w = min(250, int(w/4))
	if block_w==250:
		gap_x = int((w-4*250)/5)
	else:
		gap_x = 0

	#--- buttons and labels
	btns = [gui.Button(gap_x+int(block_w/2), h-45, "Menu", w=block_w),
			gui.Button(gap_x*4+int(block_w/2)*7, h-45, "Exit", w=block_w)]
	lbls = [gui.TextLabel(gap_x*2+int(block_w/2)*3, h-45, "Circle: 1", w=block_w),
			gui.TextLabel(gap_x*3+int(block_w/2)*5, h-45, "On move: ", w=block_w)]
			# gui.TextLabel(int(board_w/2)+20, int(board_h/2)+20, "", w=board_w-20*2)]

	main = gui.MenuWindow(win, btns=btns, lbls=lbls, color=(255,255,255))

	imgs = load_imgs()

	#--- init draw
	main.draw(pygame.mouse.get_pos())

	pygame.draw.rect(win, (0,0,0), hand_rect, 1)
	pygame.draw.rect(win, (0,0,0), trash_rect, 1)
	pygame.draw.rect(win, (0,0,0), pile_rect, 1)

	pygame.display.update()

	clock = pygame.time.Clock()
	run, exit = False, False

	#--- waiting loop for game to start
	wait = True
	while wait:
		clock.tick(60)

		game = netw.send_recv({"get":None})

		if game=="close":
			wait = False

		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				exit = True
				wait = False

			if event.type==pygame.MOUSEBUTTONDOWN:
				if btns[-1].rect.collidepoint(event.pos):
					wait = False

		if game.ready:
			run = True
			wait = False

	cards2imgs = True
	update_window = True
	sent_card_to_trash = False
	for_board = []

	#--- main game loop
	while run:
		clock.tick(60)

		game = netw.send_recv({"get":None})

		if game=="close":
			run = False
			break

		events = pygame.event.get()
		for event in events:
			if event.type==pygame.QUIT:
				exit = True
				run = False

			if event.type==pygame.MOUSEBUTTONDOWN:
				if btns[-1].rect.collidepoint(event.pos):
					run = False

		"""
		When something changes, redraw window objects.

		Changes are:
			-- player grabed the card from pile/trash/hand
			-- player openes his cards on board
			-- other player is opening his cards
		"""
		if game.players[pID].game_update_win or update_window:
			#--- first draw window then later elements
			main.draw(pygame.mouse.get_pos())

			#--- draw cards on board
			if len(game.board)>0:
				dx, dy = 0, 0
				for card_list in game.board:
					for card in card_list:
						win.blit(imgs[card.symbol], (30+dx, 30+dy))
						dx += 25
					dx += card_w
					if (dx+25+3*card_w)>board_w:
						dy += card_h + 25
			
			#--- draw trash card
			if len(game.trash)>0:
				win.blit(imgs[game.trash[-1].symbol], (trash_rect.x, trash_rect.y))
			#--- draw hand card
			if game.hand!=None:
				win.blit(imgs[game.hand.symbol], (hand_rect.x, hand_rect.y))
			#--- draw pile card
			win.blit(imgs["blue_back"], (pile_rect.x, pile_rect.y))
			
			#--- update users cards with images and their position
			if cards2imgs:
				cards = game.players[pID].cards
				get_imgs_for_cards(cards, imgs, board_rect)
				cards2imgs = False
			draw_user_cards(win, cards)

			#--- draw rectangles for pile/hand/trash
			pygame.draw.rect(win, (0,0,0), hand_rect, 1)
			pygame.draw.rect(win, (0,0,0), trash_rect, 1)
			pygame.draw.rect(win, (0,0,0), pile_rect, 1)

			pygame.display.update()
			
			# netw.send({"updated":True})
			update_window = False

		if not game.moved[pID]:
			#--- events handling
			for event in events:
				if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
					#--- grab new card
					if not game.players[pID].got_new_card:
						if pile_rect.collidepoint(event.pos):
							netw.send({"moved":"pile"})
							cards2imgs = True
						if hand_rect.collidepoint(event.pos):
							netw.send({"moved":"hand"})
							cards2imgs = True
						if trash_rect.collidepoint(event.pos):
							netw.send({"moved":"trash"})
							cards2imgs = True
					#--- if we have new card, play
					else:
						for card in cards[::-1]:
							if card.active:
								if trash_rect.collidepoint(event.pos):
									card.img = None
									card.rect = None
									card.active = False
									netw.send({"moved":"end", "card":card})
									cards2imgs = True
									for_board = []
									break
								if card.rect.collidepoint(event.pos):
									card.active = False
									card.rect.y += 25
									break
							else:
								if card.rect.collidepoint(event.pos):
									card.active = True
									card.rect.y -= 25
									update_window = True
									for_board.append(card)
									break
						#--- send cards to board (aka open cards)
						if board_rect.collidepoint(event.pos):
							if check_card_set(for_board):
								for card in for_board:
									card.img = None
									card.active = False
								netw.send({"moved":"opened", "cards":for_board})
								cards2imgs = True
								for_board = []
							else:
								for card in for_board:
									card.active = False
									card.rect.y += 25
								for_board = []
								update_window = True

	game = netw.send({"exit":None})

	return exit

