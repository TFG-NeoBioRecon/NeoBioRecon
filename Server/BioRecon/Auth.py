from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from BioRecon.Log import Logdate

def Kick(conn, addr):
    print(Logdate(), "[LOG]",addr[0], "Successfully Kicked!")
    conn.close()

def Auth(conn, addr):

    session_key = get_random_bytes(16)
    print(Logdate(), "[LOG]", addr[0], "Getting public key")

    conn.settimeout(2)
    try:
        pubkey = RSA.import_key(conn.recv(1024))
        print(pubkey)
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

    # Check if public key is in auth file
    with open('authorized_keys') as authk_file:
        if pubkey.export_key().decode("ascii") not in authk_file.read():
            print(Logdate(), "[ERROR]", addr[0],'Public key not found in auth file')
            conn.send(b"flag{Leave_my_server_alone}")
            Kick(conn, addr)
            return False

    cipher = PKCS1_OAEP.new(pubkey)
    conn.send((cipher.encrypt(session_key)))

    # Recive the nonce and make the auth challenge
    nonce = conn.recv(1024)
    cipher = AES.new(session_key, AES.MODE_EAX, nonce)
    encrypter = AES.new(session_key, AES.MODE_EAX, nonce=nonce)
    client_session_key = cipher.decrypt(conn.recv(16))
    print(client_session_key)
    if client_session_key == session_key:
        print(Logdate(), "[LOG]", addr[0], "authenticated successfully")
        return True, (conn, addr, cipher, encrypter)

    else:
        print(Logdate(), "[ERROR]", addr[0],"Failed to decrypt chiphertext ", addr[0])
        conn.send(b"flag{Leave_my_server_alone}")
        Kick(conn, addr)
        return False, ()