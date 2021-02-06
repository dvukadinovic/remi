import pygame

import gui
from network import Network

#=============================================================================#
#=============------------- Connect window function -------------=============#
#=============================================================================#

def establish_connection(boxes, lbls):
	"""
	Button action when user clicks on to 'Connect'
	"""
	addr = boxes[0].text
	
	try:
		port = int(boxes[1].text)
		try:
			#--- if entered port number is good (integer) try to connect
			if not gui.MenuWindow.netw:
				#--- if there is no Network object, create one
				gui.MenuWindow.netw = Network(addr,port)
				lbls[0].text = "Connected successfully"
			elif gui.MenuWindow.netw.connected:
				#--- if we are connected, inform the user
				lbls[0].text = "Already connected"
		except:
			lbls[0].text = "Server not running / check IP and port number"
	except:
		lbls[0].text = "Bad port number (not int)"

def destroy_connection(lbls):
	"""
	Button action when user clicks on to 'Disconnect'
	"""
	try: 
		if gui.MenuWindow.netw.connected:
			#--- if we are connected, disconnect the user
			gui.MenuWindow.netw.send("close")
			gui.MenuWindow.netw.close()
			gui.MenuWindow.netw = None
			lbls[0].text = "Disconnected"
		else:
			lbls[0].text = "Already disconnected"
	except:
		lbls[0].text = "No active connection to server"

def connect_menu(win):
	"""
	Main function which sets the 'connect' window
	"""
	w, h = win.get_size()

	btns = [gui.Button(130, int(h/2)-20, "Connect", align="l"),
			gui.Button(130, int(h/2)+20, "Disconnect", align="l"),
			gui.Button(130, h-45, "Back", align="l")]
	boxes = [gui.TextBox(int(w/2), int(h/2)-20, text="0.0.0.0"),
			 gui.TextBox(int(w/2), int(h/2)+20, text="5555")]
	lbls = [gui.TextLabel(int(w/2), int(h/2)-70, text="", color=(200,0,0), wrap=False)]

	surf = pygame.Surface((250,h))
	surf.set_alpha(55)
	surf.fill((0,0,0))

	menu = gui.MenuWindow(win, btns=btns, boxes=boxes, lbls=lbls, surfs=[surf])
	
	try:
		if gui.MenuWindow.netw.connected:
			lbls[0].text = "Connected"
	except:
		lbls[0].text = "No active connection to server"

	clock = pygame.time.Clock()
	run, exit = True, False
	while run:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				exit = True

			if event.type == pygame.MOUSEBUTTONDOWN:
				if btns[-1].rect.collidepoint(event.pos):
					run = False
				if btns[0].rect.collidepoint(event.pos):
					establish_connection(boxes, lbls)
				if btns[1].rect.collidepoint(event.pos):
					destroy_connection(lbls)

			for box in boxes:
				box.handle_event(event)

		menu.draw(pygame.mouse.get_pos())
		pygame.display.update()

	return exit

#=================================--- end ---=================================#

#=============================================================================#
#============------------ Create game window function ------------============#
#=============================================================================#

def send_init_data(boxes, lbl):

	Nplayers = int(boxes[1].text)
	if Nplayers>6 or Nplayers<2:
		lbl.text = "Number of players out of interval [2,6]"
		return False

	Njokers = int(boxes[2].text)
	if Njokers>8 or Njokers<4:
		lbl.text = "Number of jokers out of interval [4,8]"
		return False

	game_name = boxes[0].text
	if len(game_name)>10 and len(game_name)<2:
		lbl.text = "Length of game name out of interval [2,10]"
		return False

	player_name = boxes[3].text
	if len(player_name)>10 and len(player_name)<2:
		lbl.text = "Length of player name out of interval [2,10]"
		return False

	try:
		if gui.MenuWindow.netw.connected:
			gui.MenuWindow.netw.send("create")
			msg = gui.MenuWindow.netw.send_recv([Nplayers, Njokers, game_name, player_name])
			if msg=="exists":
				lbl.text = "Game with given name already exist"
				return False
			elif msg=="init_error":
				lbl.text = "Bad game inital data sent..."
				return False
			else:
				lbl.text = "Starting the game..."
				return msg
		else:
			lbl.text = "Not connected to game server"
			return False	
	except:
		lbl.text = "No existing Network object to the server"
		return False

def create_game_menu(win):
	"""
	Main function which sets the 'create game' window
	"""
	w, h = win.get_size()

	btns = [gui.Button(130, int(h/2), "Create", align="l"),
			gui.Button(130, h-45, "Back", align="l")]
	boxes = [gui.TextBox(630, int(h/2)-60, text="pica"),
			 gui.TextBox(630, int(h/2)-20, text="2"),
			 gui.TextBox(630, int(h/2)+20, text="8"),
			 gui.TextBox(630, int(h/2)+60, text="Dusan")]
	lbls = [gui.TextLabel(375, int(h/2)-60, text="Game name", align="r"),
			gui.TextLabel(375, int(h/2)-20, text="Max players", align="r"),
			gui.TextLabel(375, int(h/2)+20, text="Number of jokers", align="r"),
			gui.TextLabel(375, int(h/2)+60, text="Player name", align="r"),
			gui.TextLabel(int(w/2), int(h/2)-110, text="Set the game initial data", color=(200,0,0))]
	surf = pygame.Surface((250,h))
	surf.set_alpha(55)
	surf.fill((0,0,0))

	menu = gui.MenuWindow(win, btns=btns, boxes=boxes, lbls=lbls, surfs=[surf])

	clock = pygame.time.Clock()
	run, exit, start, pID = True, False, False, None
	while run:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				exit = True

			if event.type == pygame.MOUSEBUTTONDOWN:
				if btns[-1].rect.collidepoint(event.pos):
					run = False
				if btns[0].rect.collidepoint(event.pos):
					pID = send_init_data(boxes, lbls[-1])
					if type(pID)==int:
						start, run = True, False

			for box in boxes:
				box.handle_event(event)

		menu.draw(pygame.mouse.get_pos())
		pygame.display.update()

	if start:
		pygame.time.delay(500)

	return exit, start, pID

#=================================--- end ---=================================#

#=============================================================================#
#============------------- Join game window function -------------============#
#=============================================================================#

def join_game(boxes, lbl):
	game_name = boxes[0].text
	if len(game_name)>10 and len(game_name)<2:
		lbl.text = "Length of game name out of interval [2,10]"
		return False

	player_name = boxes[1].text
	if len(player_name)>10 and len(player_name)<2:
		lbl.text = "Length of player name out of interval [2,10]"
		return False

	try:
		if gui.MenuWindow.netw.connected:
			gui.MenuWindow.netw.send("join")
			msg = gui.MenuWindow.netw.send_recv([game_name, player_name])
			if msg=="no_game":
				lbl.text = "Game with given name does not exist"
				return False
			elif msg=="init_error":
				lbl.text = "Bad game inital data sent..."
				return False
			elif msg=="game_full":
				lbl.text = "Gamse is full"
				return False
			else:
				lbl.text = "Joining the game..."
				return msg
		else:
			lbl.text = "Not connected to game server"
			return False	
	except:
		lbl.text = "No existing Network object to the server"
		return False

def join_game_menu(win):
	"""
	Main function which sets the 'join game' window
	"""
	w, h = win.get_size()

	btns = [gui.Button(130, int(h/2), "Join game", align="l"),
			gui.Button(130, h-45, "Back", align="l")]
	boxes = [gui.TextBox(630, int(h/2)-20, text="pica"),
			 gui.TextBox(630, int(h/2)+20, text="Debora")]
	lbls = [gui.TextLabel(375, int(h/2)-20, text="Game name", align="r"),
			gui.TextLabel(375, int(h/2)+20, text="Player name", align="r"),
			gui.TextLabel(int(w/2), int(h/2)-70, text="Set the game initial data", color=(200,0,0))]
	surf = pygame.Surface((250,h))
	surf.set_alpha(55)
	surf.fill((0,0,0))

	menu = gui.MenuWindow(win, btns=btns, boxes=boxes, lbls=lbls, surfs=[surf])

	clock = pygame.time.Clock()
	run, exit, start, pID = True, False, False, None
	while run:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				exit = True

			if event.type == pygame.MOUSEBUTTONDOWN:
				if btns[-1].rect.collidepoint(event.pos):
					run = False
				if btns[0].rect.collidepoint(event.pos):
					pID = join_game(boxes, lbls[-1])
					if type(pID)==int:
						start, run = True, False

			for box in boxes:
				box.handle_event(event)

		menu.draw(pygame.mouse.get_pos())
		pygame.display.update()

	if start:
		pygame.time.delay(2000)

	return exit, start, pID

#=================================--- end ---=================================#