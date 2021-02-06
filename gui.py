import pygame

palet = [(255,127,14),(44,160,44),(0,0,160)]

class TextBox:
	"""
	Class object which represents input text box.

	Parameters:
	-----------
	x : int
	  Text box rectangle center on x asis.
	y : int
	  Text box rectangle center on y axis.
	w : int, optional
	  Text box rectangle width. Default 250.
	h : int, optional
	  Text box rectangle height. Default if set by font_size + 5.
	text : str, optional
	  Initial string in the text box. Defualt empty string.
	font_family : str, optional
	  Font family of the text. Default is "monospace".
	font_size : int, optional
	  Font size. Default is 25..
	active_color : int tuple, optional
	  Color of text and rectangle when we are typing the text.
	  Default is (160,0,0).
	inactive_color : int tuple, optional
	  Color of text and rectangle when we are not typing the text.
	  Default is (0,0,0).
	"""

	def __init__(self, x, y, w=250, h=None,
		text='', font_family="monospace", font_size=25,
		active_color=(160,0,0), inactive_color=(0,0,0),
		transparent=True, alpha=55):
		#--- font and text settings
		self.font = pygame.font.SysFont(font_family, font_size)
		# if the input text is to wide, then we reset to input text
		if self.font.size(text)[0]<w:
			self.text = text
		else:
			self.text = ""
		self.txt_surface = self.font.render(self.text, True, inactive_color)
		self.active = False

		if not h:
			h = font_size+5

		#--- rect and text color when active/inactive
		self.color_active = active_color
		self.color_inactive = inactive_color
		self.color = self.color_inactive
		#--- rect representing the text box
		font_h = self.font.size(self.text)[1]
		if font_h<h:
			self.rect = pygame.Rect(x-int(w/2), y-int(h/2), w, h)
		else:
			self.rect = pygame.Rect(x-int(w/2), y-int(h/2), w, font_h+5*2)
		self.transparent = transparent
		self.alpha = alpha

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			#--- if the user clicked on the input_box rect.
			if self.rect.collidepoint(event.pos):
				# toggle the active variable.
				self.active = not self.active
			else:
				self.active = False
			#--- change the current color of the input box.
			if self.active:
				self.color = self.color_active
			else:
				self.color = self.color_inactive
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					txt_width = self.font.size(self.text+"m")[0]
					if txt_width<self.rect.w-20:
						self.text += event.unicode
				#--- re-render the text.
				self.txt_surface = self.font.render(self.text, True, self.color_inactive)

	def draw(self, win):
		#--- blit the rect.
		pygame.draw.rect(win, self.color, self.rect, 2)
		#--- blit the transparent surface
		if self.transparent:
			s = pygame.Surface((self.rect.width,self.rect.height))
			s.set_alpha(self.alpha)
			s.fill(self.color)
			win.blit(s, (self.rect.x,self.rect.y))
		#--- blit the text.
		win.blit(self.txt_surface, 
				(self.rect.x + 10, 
				 self.rect.y + int(self.rect.h/2) - int(self.txt_surface.get_height()/2)))

class Button:
	"""
	Class object representing button in pygame. Text font family or size
	can not be changed after the button object is initialized.

	Parameters:
	-----------
	x : int
	  Rectangle center position along x axis
	y : int
	  Rectangle center position along y axis
	text : str
	  String which represents the button name
	w : int, optional
	  Rectangle width; will be larger then specified if
	  the text can no fit inside. Default value 200.
	h : int, optional
	  Rectangle height; will be larger then sepcified if
	  the text can no fit inside. Defualt value is font_size+5.
	draw_rectangle : bool, optional
	  Flag which sets if the button rectangle should be drawn. Default False.
	font_family : str, optional
	  Font family of text. Default "monospace".
	font_size : int, optinonal
	  Size of the font. Default is 25.
	txt_color : int tuple
	  Color of the text. Defualt (0,0,0).
	align : char, optional
	  Determines how the text should be horizontaly aligned inside the 
	  rectangle. "c" is center, "l" is left and "r" is right alignment.
	  Text will always be verticaly aligned. Default "c".
	hover : bool, optional
	  Determine if the rectangle and text will change the color when the
	  mouse pointer is over the button. Default false.
	hover_color : int tuple
	  Color of the rectangle and color if 'hover' is True. We need to
	  pass the mouse position to the function draw(). Default (180,0,0).
	"""
	
	def __init__(self, x, y, text, w=200, h=None, draw_rect=False,
				 font_family="monospace", font_size=25, txt_color=(0,0,0), align="c",
				 hover=False, hover_color=(180,0,0)):
		#--- text settings
		self.font  = pygame.font.SysFont(font_family, font_size)
		self.text = text
		self.text_color = txt_color
		self.color = self.text_color
		self.align = align
		if not h:
			h = font_size+5

		#--- drawing settings
		self.hover_color = hover_color
		self.draw_rect = draw_rect
		self.hover = hover
		
		#--- check if the text will fit in the rectangle
		font_w, font_h = self.font.size(text)
		if font_h<h and font_w<w:
			self.x = x - int(w/2)
			self.y = y - int(h/2)
		elif font_h>h and font_w<w:
			# add 5px belowe and above the text
			h = font_h+5*2
			self.x = x - int(w/2)
			self.y = y - int(h/2)
		elif font_h<h and font_w>w:
			# add 10px before and after the text
			w = font_w+10*2
			self.x = x - int(w/2)
			self.y = y - int(h/2)
		elif font_h>h and font_w>w:
			# add 10px before and after the text
			# add 5px belowe and above the text
			w = font_w+10*2
			h = font_h+5*2
			self.x = x - int(w/2)
			self.y = y - int(h/2)
		self.rect = pygame.Rect(self.x, self.y, w, h)

	def draw(self, win, pos):
		"""
		Blit the text on the display 'win' with the given alignment.
		If the hover is True and we are parsing the mouse position it
		will change the color of the rectangle (if we are drawing it)
		and of text.
		"""
		#--- check if we are hovering over button
		if self.hover:
			self.on_hover(pos)
		#--- button label and alignment of the text
		self.label = self.font.render(self.text, True, self.color)
		if self.align=="c":
			win.blit(self.label, 
				(self.x + int(self.rect.w/2) - int(self.label.get_width()/2), 
				 self.y + int(self.rect.h/2) - int(self.label.get_height()/2)))
		elif self.align=="l":
			# we add here 10px shift to the text
			win.blit(self.label,
				(self.x + 10,
				self.y + int(self.rect.h/2) - int(self.label.get_height()/2)))
		elif self.align=="r":
			# we add here 10px shift to the text
			win.blit(self.label,
				(self.x + self.rect.w - self.label.get_width() - 10,
				 self.y + int(self.rect.h/2) - int(self.label.get_height()/2)))
		#--- check if we should draw and rectangle around text
		if self.draw_rect:
			pygame.draw.rect(win, self.color, self.rect, 2)

	def on_hover(self, pos):
		# if we are hovering over button, change the color
		# of the rectangle and text
		if self.rect.collidepoint(pos):
			self.color = self.hover_color
		else:
			self.color = self.text_color

class TextLabel:
	"""
	Class which represents Text Label object.

	Parameters:
	-----------
	x : int
	  Text box rectangle center on x asis.
	y : int
	  Text box rectangle center on y axis.
	text : str
	  Initial string in the text box.
	w : int, optional
	  Text box rectangle width. Default 250.
	h : int, optional
	  Text box rectangle height. Default if font_size + 5.
	font_family : str, optional
	  Font family of the text. Default is 'monospace'.
	font_size : int, optional
	  Font size. Default is 25.
	color : int tuple, optional
	  Text color. Default (0,0,0).
	align : char, optional
	  Text alignment. Default "c".
	wrap : bool, optional
	   Flag for wrapping text or not. Default False.
	draw_rect : bool, optional
	  Flag to draw or not the rectangle around the text. Default False.

	To add/change:
	- to break the text in multilines if it is to wide
	"""
	
	def __init__(self, x, y, text, w=250, h=None, 
				font_family="monospace", font_size=25, color=(0,0,0), 
				align="c", wrap=False, draw_rect=False):
		#--- text intialization
		self.font  = pygame.font.SysFont(font_family, font_size)
		self.text = text
		self.color = color
		self.align = align
		self.wrap = wrap
		if not h:
			self.h = font_size+5
		else:
			self.h = h

		#--- rectangle definition
		self.x = x - int(w/2)
		self.y = y - int(self.h/2)
		self.rect = pygame.Rect(self.x, self.y, w, self.h)
		self.draw_rect = draw_rect

	def draw(self,win):
		#--- split text if it is wider then rectangle
		if self.wrap:
			wt,_ = self.font.size(self.text)
			nrows = wt//self.rect.w + 1
			#--- rectangle height = num. of rows x elementar height
			self.rect.h = nrows * self.h
			
			#--- set y position of rectangles corner (left-up corner)
			self.y = self.rect.centery - int(self.rect.h/2)
			self.rect.y = self.y

			#--- split text into 'nrows'
			words = self.text.split(" ")
			lines = []
			line = ""
			for word in words:
				if self.font.size(line+word)[0]<self.rect.w:
					line += word + " "
				else:
					lines.append(line)
					line = word + " "
			lines.append(line)
			print(lines)
		else:
			nrows = 1
		#--- text label
		self.label = self.font.render(self.text, True, self.color)
		if self.align=="l":
			win.blit(self.label,
				(self.x + 10, 
				 self.y + int(self.rect.h/2) - int(self.label.get_height()/2)))
		if self.align=="r":
			win.blit(self.label,
				(self.x + self.rect.w - self.label.get_width() - 10,
				 self.y + int(self.rect.h/2) - int(self.label.get_height()/2)))
		if self.align=="c":
			win.blit(self.label,
				(self.x + int(self.rect.w/2) - int(self.label.get_width()/2), 
				 self.y + int(self.rect.h/2) - int(self.label.get_height()/2)))
		if self.draw_rect:
			pygame.draw.rect(win, self.color, self.rect , 2)

class MenuWindow:
	netw = None

	def __init__(self, win, btns=None, lbls=None, boxes=None, surfs=None,
			color=palet[0]):
		self.win = win
		self.obj = {"buttons"  : btns,
					"lables"   : lbls,
					"txtboxes" : boxes,
					"surfaces" : surfs}
		self.bkg_color = color

	def draw(self, pos):
		self.win.fill(self.bkg_color)
		#--- draw buttons
		if self.obj["buttons"]:
			for btn in self.obj["buttons"]:
				btn.draw(self.win, pos)
		#--- draw labels
		if self.obj["lables"]:
			for lbl in self.obj["lables"]:
				lbl.draw(self.win)
		#--- draw text boxes
		if self.obj["txtboxes"]:
			for box in self.obj["txtboxes"]:
				box.draw(self.win)
		#--- draw surfaces
		# if self.obj["surfaces"]:
		# 	for surf in self.obj["surfaces"]:
		# 		self.win.blit(surf, (0,0))
