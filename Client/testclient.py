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
import threading 
from ledriver import opendoor
from ledriver import YellowBlink
import os
import sys

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

def SocketCreation(pubkey):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.17.202', 8181))
    connection = client_socket.makefile('wb')
    client_socket.send(pubkey.exportKey())
    return(client_socket,connection)

def SessionkeyExchange(privkey,client_socket):

    cipher = PKCS1_OAEP.new(privkey)

    #session_key
    session_key = (cipher.decrypt(client_socket.recv(1024)))
    cipher = AESCipher(session_key)
    client_socket.send(cipher.nonce)
    client_socket.send(cipher.encrypt(session_key))
    d_cipher = AES.new(session_key, AES.MODE_EAX, cipher.nonce)
    return(cipher,session_key,d_cipher)

def Camset():

    cam = cv2.VideoCapture(0,cv2.CAP_V4L2)
    cam.set(15, 19980);
    cam.set(12, 14500);
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    img_counter = 0
    return(cam,encode_param,img_counter)


# Using the server function to display webcam content
def ShowFrame(window, frame):
    # Render frames in cv2 Window
    cv2.imshow(window, frame)
    cv2.waitKey(1)


def CheckAcces(conn,d_cipher):
    conn.settimeout(20)
    while True:
        try:
            data = (conn.recv(1024))
            if d_cipher.decrypt(data) == b'True':
                opendoor()
        except Exception as e:

            CheckAcces(conn,d_cipher)


def Connect(pubkey):
    
    client_socket,connection = SocketCreation(pubkey)
    return client_socket,connection
def Main(client_socket,connection,cipher):

    cam,encode_param,img_counter=Camset()

    #cipher,session_key=SessionkeyExchange(privkey,client_socket)

    room_id= b'1'
    client_socket.send(cipher.encrypt(room_id))
    while True:
        time.sleep(0.06)
        ret, frame = cam.read()
        # Calling ShowFrame function before encoding to display webcam content on client 
        #ShowFrame("",frame)
        result, frame = cv2.imencode('.jpg', frame, encode_param)    
        data = pickle.dumps(frame, 0)
        size = len(data)
        print("{}: {}".format(img_counter, size))
        payload = struct.pack(">L", size) + data
        client_socket.sendall(cipher.encrypt(payload))
            
        img_counter += 1


    client_socket.close()

def CheckConn(conn):
    while True:
        try:
            conn.send(b'')
            YellowBlink()
        except Exception as e: 
            while True:
                try: 
                    thread1.join()
                    thread2.join()
                    thread3.join()
                    time.sleep(10)
                    Init()
                except:
                    pass
            print(e) 

            
def Init():
    pubkey,privkey = Getkeys()
    client_socket,connection = Connect(pubkey)
    cipher,session_key,d_cipher=SessionkeyExchange(privkey,client_socket)
    thread1 = threading.Thread(target=CheckAcces, args=(client_socket,d_cipher,))
    thread2 = threading.Thread(target=Main, args=(client_socket, connection,cipher,))
    thread3 = threading.Thread(target=CheckConn, args=(client_socket,))
    thread3.start()
    time.sleep(2)
    thread2.start()
    time.sleep(2)
    thread1.start()

         
if __name__ == '__main__':
    Init()




    
