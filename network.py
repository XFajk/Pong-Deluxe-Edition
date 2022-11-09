import socket


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '192.168.1.13'
        self.port = 5555
        self.addr = (self.server,self.port)
        self.ID = self.connect()
        print(self.ID)

    def connect(self):
        try:
            self.client.connect(self.addr) 
            return self.client.recv(2048).decode()
        
        except socket.error as err:
            return err
        
    def send(self, data:str):
        pass



n = Network()