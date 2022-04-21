import socket
from BioRecon.Log import Logdate


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
        #os.system("taskkill /f /im python.exe")
        exit(0)
    return s

# Accept new connections
def NewConnection(s):
    while True:
        # Accepts new inbound connections
        conn,addr = s.accept()
        print(Logdate(), "[LOG]", addr[0],"Connected")
        # Returns connection object and address
        yield conn, addr


# Close socket and kill thread
def CloseConnection(conn, addr):
    print(Logdate(), "[ERROR]", addr[0], "Connection Lost ")
    # Close Connection Socket
    conn.close()
    return 0