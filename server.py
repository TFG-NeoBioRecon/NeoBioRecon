import socket
import os
import numpy as np
from _thread import *
import cv2
import pickle
import struct
from time import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

def Auth(conn, addr):
	session_key = get_random_bytes(16)
	try:
		print("Getting public key from ",addr[0])
		#Falta poner un time out o algo, un atacante puede 
		#abrir un netcat no introducir nada y denegar la conxiona clientes ya que esta no va por hilos
		pubkey = RSA.import_key(conn.recv(1024))

		#Checking if public key si found in auth file
		with open('authorized_keys') as authk_file:
			if pubkey.export_key().decode("ascii") not in authk_file.read():
				print('Public key not found in auth file')
				conn.send(b"flag{Leave_my_server_alone}")
				conn.close()
				print(addr[0], "Successfully Kicked!")
				return True


		cipher = PKCS1_OAEP.new(pubkey)
		conn.send((cipher.encrypt(session_key)))
		print("Ciphered session key sent to ",addr[0])

		if conn.recv(1024) != session_key:
			print("Failed to decrypt chiphertext ", addr[0])
			conn.send(b"flag{Leave_my_server_alone}")
			conn.close()
			print(addr[0], "Successfully Kicked!")
			return True

		else:
			print(addr[0], "authenticated successfully")
		return True

	except Exception as e:
		print('ERROR:',str(e),"from", addr[0])
		conn.close()
		return True


# Iterator,k Accepts and returns new connections
def ConnectionHandler(s):
	while True:
		# Accepts new inbound connections
		conn,addr = s.accept()
		print("Connection From ", addr[0])

		#                             Avoid yield
		if Auth(conn, addr): continue
		# Returns connection object and address
		yield conn, addr

# Open Socket on specified port for incoming connections
def BindSocket(HOST, PORT):

	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	try:
		print('Creating Socket')
		# Bind ip and port to socket
		s.bind((HOST,PORT))
		print('Socket bind complete')
		# Listens for incoming connections
		s.listen(10)
		print(f'Socket now listening on port {HOST}:{PORT}')

	# When Bind Fails
	except socket.error as e:
		print(f"SOCKET ERROR, port {PORT} already taken?")
		# debug, kills python, change python.exe to current python version
		os.system("taskkill /f /im python.exe")
		exit(0)
	return s


# Iterator, return frames sent by the client.
def ReceiveFrames(conn, addr):
	data = b""
	payload_size = struct.calcsize(">L")
	first_time = True

	while True:
		# Fucking Magic basically
		while len(data) < payload_size:
			# return 0 when connection dies
			try:
				newdata = conn.recv(4096)
				if newdata == b'':
					return 0
				data += newdata
			except:
				return 0
		
		# Camera is slower than tcp tunnel.
		if first_time == True:
			print("Reciving Frames From " + str(addr[0]))
			first_time = False

		# Calculate size of data
		packed_msg_size = data[:payload_size]
		data = data[payload_size:]
		msg_size = struct.unpack(">L", packed_msg_size)[0]
		
		# Receive data until size matches
		while len(data) < msg_size:
			data += conn.recv(4096)

		# Formats data to unpickle
		frame_data = data[:msg_size]
		data = data[msg_size:]

		# ##############################################
		# #            FIX PICKLE.LOAD RCE             #
		# ##############################################

		# Frame gets deserialized and loadad from server
		frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
		frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
		yield frame


# Close socket and kill thread
def CloseConnection(conn, addr, window):
	# Close cv2 window
	try:
		cv2.destroyWindow(window)
	except:
		print("can't close window. webcam error?", addr[0])
	print("Connection Lost ", addr[0])
	# Close Connection Socket
	conn.close()
	return 0


# Show cv2 Window with frames in real time
def ShowFrame(window, frame):
	# Render frames in cv2 Window
	cv2.imshow(window, frame)
	cv2.waitKey(1)


# Main Execution
def Main(conn, addr):
	window = f"Recognition {time()}"
	# Get frames from client
	for frame in ReceiveFrames(conn, addr):
		ShowFrame(window, frame)
		# ====== MAIN EXECUTION IN DIFFERENT PY HERE ======

	return CloseConnection(conn, addr, window)

# Setup the server and wait for Clients
def Server():
	HOST='127.0.0.1'
	PORT=8181
	# Create Socket and listen
	s = BindSocket(HOST, PORT)
	# For every new client
	for conn, addr in ConnectionHandler(s):
		# Starts a Main() Thread
		start_new_thread(Main,(conn,addr))

if __name__ == '__main__':
	Server()












