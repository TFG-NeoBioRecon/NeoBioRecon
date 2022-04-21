from BioRecon.Log import Logdate
import pickle
import struct
import cv2


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

        # Frame gets deserialized and loadad from server
        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        yield frame