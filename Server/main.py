from BioRecon.ConnectionHandler import BindSocket, NewConnection, CloseConnection
from BioRecon.Auth import Auth
from BioRecon.CV2Frames import ReceiveFrames
from BioRecon.Recon import Recognizer
from BioRecon.Log import Logdate
from BioRecon.ReconDB import Query
from _thread import start_new_thread as thread

HOST = "0.0.0.0"
PORT = 8181

# Main Recognition
def NeoBioRecon(conn, addr, cipher, encrypter):
    room_id = cipher.decrypt(conn.recv(1024))
    print(f"Room id: {room_id}")

    # Frames received 
    for frame in ReceiveFrames(conn, addr, cipher):
        uid = Recognizer(frame)
        # User has been identified
        if uid != None:

            # If User belongs to the room
            if Query(uid, room_id):
                conn.send(encrypter.encrypt(b'True'))
                print(Logdate(), "[LOG] Authorized opening door")

            else:
                print(Logdate(), "[LOG] Unauthorized")
                conn.send(b'')

    return CloseConnection(conn, addr)


if __name__ == '__main__':
    # Create socket and listen
    s = BindSocket(HOST, PORT)
    # For every new client
    for conn, addr in NewConnection(s):
        success, args = Auth(conn, addr)
        # Check if client is authorized
        if success:
            # Start thread in main Program
            thread(NeoBioRecon, args)
        
