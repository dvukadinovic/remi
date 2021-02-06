import socket
import pickle
import sys
import struct

class Network:
	def __init__(self, server, port):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server = server
		self.port = port
		self.addr = (self.server, self.port)
		self.client.connect(self.addr)
		#--- init receive for checking if the server is running
		msg = self.recv()
		if msg=="connected":
			self.connected = True
		else:
			self.connected = False

	def send(self, data):
		try:
			#--- prefix each message with a 4-byte length (network byte order)
			msg = pickle.dumps(data)
			aux = len(msg)
			msg = struct.pack('>I', len(msg)) + msg
			self.client.sendall(msg)
			self.connected = True
		except:
			print("[NETWORK] failed to send data")
			self.close()

	def recv(self):
		try:
			#--- read message length and unpack it into an integer
			raw_msglen = self.recvall(4)
			if not raw_msglen:
				return None
			msglen = struct.unpack('>I', raw_msglen)[0]
			#--- read the message data
			out = self.recvall(msglen)
			msg = pickle.loads(out)
			return msg
		except:
			self.close()
			return "error_recv"

	def recvall(self, n):
		#--- helper function to recv n bytes or return None if EOF is hit
		data = bytearray()
		while len(data) < n:
			packet = self.client.recv(n - len(data))
			if not packet:
				return None
			data.extend(packet)
		return data

	def send_recv(self, data):
		self.send(data)
		if self.connected:
			out = self.recv()
			return out
		else:
			return "closed"

	def close(self):
		self.client.close()
		self.connected = False
		print("[NETWORK] socket closed")