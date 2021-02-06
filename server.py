import socket
from _thread import start_new_thread
import pickle
import time
from game import Game
import sys
import struct

def send_msg(conn, data):
	msg = pickle.dumps(data)
	msg = struct.pack('>I', len(msg)) + msg
	conn.sendall(msg)

def recv_msg(conn):
	try:
		raw_msglen = recvall(conn, 4)
		if not raw_msglen:
			return None, False
		msglen = struct.unpack('>I', raw_msglen)[0]
		out = recvall(conn, msglen)
		return pickle.loads(out)
	except:
		return "error"

def recvall(conn, n):
	data = bytearray()
	while len(data) < n:
		packet = conn.recv(n - len(data))
		if not packet:
			return None
		data.extend(packet)
	return data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)

# server = "25.0.131.175" # Hamachi IP
server = "0.0.0.0"
port = 5555

try:
	s.bind((server,port))
except socket.error as e:
	print(e)
	sys.exit()

s.listen()
print("Waiting for a connection, Server Started!")

games = {}
num_of_connected = 0

def game_on(conn, pID, game_name):
	# if created/joined then start the main loop and start the game
	# else break from the thread and close the connection
	global games

	run = True
	while run:
		data = recv_msg(conn)
		if game_name in games:
			game = games[game_name]
			if "error" in data or "exit" in data:
				run = False
				break
			if "get" in data:
				send_msg(conn, game)
			if "moved" in data:
				if data["moved"]=="end":
					game.made_move(pID, data["card"])
				if data["moved"]=="pile":
					game.get_card_from_pile(pID)
				if data["moved"]=="trash":
					game.get_card_from_trash(pID)
				if data["moved"]=="hand":
					game.get_card_for_hand(pID)
				if data["moved"]=="opened":
					game.open_cards(pID, data["cards"])
			if "updated" in data:
				# game.updated_win(pID)
				game.update_players_window()
		else:
			run = False
			send_msg(conn, "close")
			break

	try:
		del games[game_name]
		print("Deleting the game: ", game_name)
	except:
		pass

def threded_client(conn, addr):
	# one infinit loop waits for game init data
	# if user creates / joins forward him to some other function which 
	# will have ininit loop in which server-client correspondance will
	# occure and the game is played.
	# I can not have sparate loop for it, because, if player exits, the connection
	# is closed and the game deleted. I want if user exits the existing game
	# just to delete it (send to server that it is closed and client is chekcing
	# if the game exists and closes if it is not existant). After it, user is
	# brought back to main menu.

	global games
	global num_of_connected
	
	num_of_connected += 1
	run = False

	#--- send user confirmation that he is connected to server
	send_msg(conn,"connected")

	#--- wait for player input (creating or joining)
	while True:
		data = recv_msg(conn)
		#--- create the new game with data input
		if data=="create":
			data = recv_msg(conn)
			if data:
				np, nj, game_name, p_name = data
				if game_name not in games:
					games[game_name] = Game(np,nj)
					pID = games[game_name].add_player(p_name)
					send_msg(conn, pID)
					print(f"[SERVER] Player '{p_name}' created the game '{game_name}'")
					game_on(conn,pID,game_name)
				else:
					send_msg(conn,"exists")
			else:
				print("[SERVER] bad receive game init data...")
				send_msg(conn,"init_error")
		#--- join the player to requested game
		elif data=="join":
			data = recv_msg(conn)
			if data:
				game_name, p_name = data
				if game_name in games:
					pID = games[game_name].add_player(p_name)
					if pID=="full":
						send_msg(conn, "game_full")
					else:
						send_msg(conn,pID)
						print(f"[SERVER] Player '{p_name}' joined the game '{game_name}'")
						game_on(conn, pID, game_name)
				else:
					send_msg(conn,"no_game")
			else:
				print("[SERVER] bad receive game init data...")
				send_msg(conn,"init_error")
		#--- client is closing the connection
		elif data=="close":
			break
		#--- bad receive of data
		elif data=="error":
			print("[SERVER] could not receive the init message from client ", conn)
			break
		#--- garbage can; should never enter here...
		else:
			# print("[SERVER] Client sent something unrecognized...")
			pass

	#--- delete the game from active games
	try:
		num_of_connected -= 1
		print("Still active players: ", num_of_connected)
		print("Still active games: ", len(games))
	except:
		pass

	print("Closing connection to: ", addr)
	print()
	conn.close()

while True:
	conn, addr = s.accept()
	print("\nConetcted to: ", addr)
	start_new_thread(threded_client, (conn,addr))