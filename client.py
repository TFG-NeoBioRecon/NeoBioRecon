import cv2
import socket
import struct
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Blowfish
from os.path import exists
import time
from Crypto.Cipher import AES

if not exists("pub_key") or not exists("priv_key") :
    print("Keys not found, generating new kay pair")
    keypair = RSA.generate(1024) 
    pubkey_file = open('pub_key','wb')
    pubkey_file.write(keypair.publickey().export_key())
    pubkey_file.close
    priv_file = open('priv_key','wb')
    priv_file.write(keypair.exportKey())
    priv_file.close
    print("Keys generated in local working directory")


print("Keys found, reading from local working directory")
with open('pub_key', mode='r') as pubkey_file:
    pubkey = RSA.import_key(pubkey_file.read())
    pubkey_file.close
with open('priv_key', mode='r') as priv_file:
        privkey = RSA.import_key(priv_file.read())
        priv_file.close



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8181))
connection = client_socket.makefile('wb')
client_socket.send(pubkey.exportKey())

cipher = PKCS1_OAEP.new(privkey)

session_key = (cipher.decrypt(client_socket.recv(1024)))

client_socket.send(session_key)

cam = cv2.VideoCapture(0)

cam.set(15, 19980);
cam.set(12, 14500);

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
img_counter = 0


#session_key
cipher = AESCipher(session_key)
client_socket.send(cipher.nonce)


while True:
    
    ret, frame = cam.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    data = pickle.dumps(frame, 0)

    size = len(data)
    print("{}: {}".format(img_counter, size))
    payload = struct.pack(">L", size) + data
    client_socket.sendall(cipher.encrypt(payload))
    img_counter += 1

client_socket.close()
