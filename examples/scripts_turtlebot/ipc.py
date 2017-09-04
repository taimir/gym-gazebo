import pickle
from multiprocessing.connection import Listener, Client


class SLAMServer:
    def __init__(self, port=6000, bind_adress='0.0.0.0'):
        address = (bind_adress, port)

        self.listener = Listener(address, authkey=b'SLAM!')
        self.port = port
        self.bind_adress = bind_adress

        self.conn = self.listener.accept()
        print('connection accepted from {}'.format(self.listener.last_accepted))

    def receive_data(self):

        while True:
            data_bytes = self.conn.recv_bytes()
            data = pickle.loads(data_bytes)
            yield data

    def close(self):
        self.conn.close()
        self.listener.close()


class SLAMClient:
    def __init__(self, port=6000, server_ip='localhost'):
        address = (server_ip, port)

        self.conn = Client(address, authkey=b'SLAM!')
        self.port = port
        self.server_ip = server_ip

    def send_data(self, data):
        data_bytes = pickle.dumps(data, protocol=2)
        self.conn.send_bytes(data_bytes)

    def close(self):
        self.conn.close()
