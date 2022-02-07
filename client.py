import cv2
import socket
import struct
import pickle


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8181))
connection = client_socket.makefile('wb')

PASSWORD = b"change_me"
client_socket.send(PASSWORD)

cam = cv2.VideoCapture(0)

cam.set(15, 19980);
cam.set(12, 14500);

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
img_counter = 0

while img_counter < 100:
	ret, frame = cam.read()
	result, frame = cv2.imencode('.jpg', frame, encode_param)
	
	data = pickle.dumps(frame, 0)
	size = len(data)

	print("{}: {}".format(img_counter, size))
	client_socket.sendall(struct.pack(">L", size) + data)
	img_counter += 1

client_socket.close()
cam.release()