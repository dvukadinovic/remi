#--- setting the starting window position on the screen
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1000,250)
import sys

#--- initialize the pygame module
import pygame
pygame.init()
pygame.font.init()
pygame.mixer.quit()

#--- handmade modules for the game
import gui
import menus
import play

def define_window_wize():
	"""
	  make a screen (size based on user display resolution)

	  There is no need to go more then 80% of the display size.
	  Some users may have big menu bars or something else, so this
	  is compromise between size and seeing conditions.

	  Maybe to go for a full screen (window mode)?

	  The default w/h is 1024/768. Check the window size before creating the one. This
		is the minimum which I will support :)
	"""
	info = pygame.display.Info()
	width = info.current_w
	height = info.current_h
	aspect = width/height
	width = int(0.8*width)
	height = int(0.8*height)

	if width<1024 or height<768:
		win = pygame.display.set_mode((300,300))
		win.fill((255,255,255))
		#--- set text informing that we are not supporting this size
		font = pygame.font.SysFont("monospace", 20)
		lbl1 = font.render("Window size is", True, (0,0,0))
		lbl2 = font.render("not supported", True, (0,0,0))
		win.blit(lbl1, (50,120))
		win.blit(lbl2, (52,150))
		pygame.display.update()
		pygame.time.delay(2000)
		sys.exit()
	else:
		w, h = width,height
	
	w, h = 1024,768

	return w, h

w, h = define_window_wize()
win = pygame.display.set_mode((w,h))

#--- set the clock of the game
clock = pygame.time.Clock()

#--- create main_menu
btns = [gui.Button(130, int(h/2)-35, "Create", align="l"),
		gui.Button(130, int(h/2), "Join", align="l"),
		gui.Button(130, int(h/2)+35, "Connection", align="l"),
		gui.Button(130, h-45, "Exit", align="l")]
surf = pygame.Surface((250,h))
surf.set_alpha(55)
surf.fill((0,0,0))

menu = gui.MenuWindow(win, btns=btns, surfs=[surf])

pID = 0
run, start = True, False
while run:
	clock.tick(60)

	#--- check if we are exiting the game
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			#--- create the new game
			if btns[0].rect.collidepoint(event.pos):
				exit, start, pID = menus.create_game_menu(win)
				if exit:
					run = False
			#--- join to one of the existing games
			elif btns[1].rect.collidepoint(event.pos):
				exit, start, pID = menus.join_game_menu(win)
				if exit:
					run = False
				pass
			#--- connect to the server
			if btns[2].rect.collidepoint(event.pos):
				exit = menus.connect_menu(win)
				if exit:
					run = False
			#--- exit game
			elif btns[3].rect.collidepoint(event.pos):
				run = False

	if start:
		#--- run the game!
		exit = play.play(win,gui.MenuWindow.netw,pID)
		start = False
		if exit:
			run = False

	#--- draw on the screen
	menu.draw(pygame.mouse.get_pos())
	pygame.display.update()

if gui.MenuWindow.netw:
	gui.MenuWindow.netw.send("close")
	gui.MenuWindow.netw.close()

#--- when we exit the loop we are out of the game
pygame.quit()