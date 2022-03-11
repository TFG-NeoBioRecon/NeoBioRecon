import socket
import os
import numpy as np
from _thread import *
import cv2
import pickle
import struct
import time
import sys
import traceback
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Cipher import Blowfish
from Crypto.Cipher import AES

def Logdate():
    now = datetime.now()
    return f'[{now.strftime("%d/%m/%y %H:%M:%S")}]'

def Kick(conn, addr):
    print(Logdate(), "[LOG]",addr[0], "Successfully Kicked!")
    conn.close()


def Auth(conn, addr):

    session_key = get_random_bytes(16)
    print(Logdate(), "[LOG]", addr[0], "Getting public key")

    conn.settimeout(2)
    try:
        pubkey = RSA.import_key(conn.recv(1024))
    except socket.timeout:
        print(Logdate(), "[ERROR]", addr[0], "didn't receive RSA key on time")
        Kick(conn, addr)
        return False
    except ValueError as ve:
        print(Logdate(), "[ERROR]", addr[0], ve)
        Kick(conn, addr)
        return False
    except ConnectionResetError as e:
        print(Logdate(), "[ERROR]", addr[0], e)
        Kick(conn, addr)
        return False
    conn.settimeout(None)


    #Checking if public key si found in auth file

    with open('authorized_keys') as authk_file:
        if pubkey.export_key().decode("ascii") not in authk_file.read():
            print(Logdate(), "[ERROR]", addr[0],'Public key not found in auth file')
            conn.send(b"flag{Leave_my_server_alone}")
            Kick(conn, addr)
            return False

    cipher = PKCS1_OAEP.new(pubkey)
    conn.send((cipher.encrypt(session_key)))

    if conn.recv(1024) == session_key:
        print(Logdate(), "[LOG]", addr[0], "authenticated successfully")
        # get nonce
        nonce = conn.recv(1024)
        print(nonce)
        cipher = AES.new(session_key, AES.MODE_EAX, nonce)
        Main(conn, addr, cipher)
        return True

    else:
        print(Logdate(), "[ERROR]", addr[0],"Failed to decrypt chiphertext ", addr[0])
        conn.send(b"flag{Leave_my_server_alone}")
        Kick(conn, addr)
        return False

# Iterator,k Accepts and returns new connections
def ConnectionHandler(s):
    while True:
        # Accepts new inbound connections
        conn,addr = s.accept()
        print(Logdate(), "[LOG]", addr[0],"Connected")

        #                             Avoid yield
        #if not Auth(conn, addr): continue
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
def ReceiveFrames(conn, addr, cipher):
    data = b""
    payload_size = struct.calcsize(">L")
    first_time = True
    


    while True:
        # Fucking Magic basically
        while len(data) < payload_size:
            # return 0 when connection dies
            try:
                newdata = cipher.decrypt(conn.recv(4096))
                if newdata == b'':
                    return 0
                data += newdata
            except:
                return 0
        
        # Camera is slower than tcp tunnel.
        if first_time == True:
            print(Logdate(), "[LOG]", addr[0], "Reciving Frames")
            first_time = False

        # Calculate size of data
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        
        # Receive data until size matches
        while len(data) < msg_size:
            data += cipher.decrypt(conn.recv(4096))

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
    print(Logdate(), "[ERROR]", addr[0], "Connection Lost ")
    # Close Connection Socket
    conn.close()
    return 0



# Show cv2 Window with frames in real time
def ShowFrame(window, frame):
    # Render frames in cv2 Window
    cv2.imshow(window, frame)
    cv2.waitKey(1)


# Main Execution
def Main(conn, addr, cipher):
    window = f"Recognition {time.time()}"
    
    # Get frames from client
    for frame in ReceiveFrames(conn, addr, cipher):
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
        print("Happened")
        #start_new_thread(Main,(conn,addr))
        start_new_thread(Auth,(conn,addr))

if __name__ == '__main__':
    Server()
