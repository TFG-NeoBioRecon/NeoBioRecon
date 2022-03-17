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

# Create a window to display on client side
window = f"Recognition {time.time()}"

def AESCipher(key):
    cipher = AES.new(key, AES.MODE_EAX)
    return cipher

def Getkeys():
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
    return(pubkey,privkey)

# Call the function getkeys 

pubkey,privkey = Getkeys()

def SocketCreation():
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8181))
    connection = client_socket.makefile('wb')
    client_socket.send(pubkey.exportKey())
    return(client_socket,connection)

client_socket,connection = SocketCreation()

def SessionkeyExchange():

    cipher = PKCS1_OAEP.new(privkey)

    #session_key
    session_key = (cipher.decrypt(client_socket.recv(1024)))
    cipher = AESCipher(session_key)
    client_socket.send(cipher.nonce)
    client_socket.send(cipher.encrypt(session_key))
    return(cipher,session_key)

cipher,session_key=SessionkeyExchange()

def Camset():

    cam = cv2.VideoCapture(0)
    cam.set(15, 19980);
    cam.set(12, 14500);
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    img_counter = 0
    return(cam,encode_param,img_counter)
cam,encode_param,img_counter=Camset()

# Using the server function to display webcam content
def ShowFrame(window, frame):
    # Render frames in cv2 Window
    cv2.imshow(window, frame)
    cv2.waitKey(1)

while True:
    
    ret, frame = cam.read()
    # Calling ShowFrame function before encoding to display webcam content on client 
    ShowFrame(window,frame)
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    
    data = pickle.dumps(frame, 0)
    size = len(data)
    print("{}: {}".format(img_counter, size))
    payload = struct.pack(">L", size) + data
    client_socket.sendall(cipher.encrypt(payload))

    img_counter += 1

client_socket.close()
