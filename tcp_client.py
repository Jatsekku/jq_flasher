import socket
import os
from tqdm import tqdm
import math

CMDSTRING="SENDSTRING"
CMDFILE="SENDFILE"
CMDQUIT="QUIT"
SEPARATOR="###"

class client:
    def __init__(self, address, port=50000, buffersize=1024):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address=address
        self.port=port

    def init_connection(self):
        self.socket.connect((self.server_address, self.port))

    def build_msg (self, cmd, arg1, arg2, arg3):
        return cmd+SEPARATOR+arg1+SEPARATOR+arg2+SEPARATOR+arg3

    def send_data(self, data):#bytes
        self.socket.sendall(data)
    
    def send_string(self, string):
        cmd=self.build_msg(CMDSTRING,string," "," ") #sending payload as arg1
        self.socket.sendall(cmd.encode('utf-8'))

    def send_file(self, filepath, server_filename):
        filetosend=open(filepath,'rb') #b is for binary
        filesize=os.path.getsize(filepath)
        chunks_amount=str(math.ceil(filesize/self.buffersize))
        cmd=self.build_msg(CMDFILE,server_filename,chunks_amount,str(self.buffersize))
        self.socket.sendall(cmd.encode('utf-8'))
        #file sending
        for it in tqdm(range(0, filesize, self.buffersize), desc="sending file"): #tqdm is for progress bar
            buff=filetosend.read(self.buffersize)
            self.socket.sendall(buff)    

    def close_comm(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()

    def cmd_close_server(self):
        cmd=self.build_msg(CMDQUIT," "," "," ")
        self.socket.sendall(cmd.encode('utf-8'))

#example code:
client=client('192.168.1.16')
client.init_connection()
#after init, send command to a server. Uncomment one.
#client.send_file('testjpg.JPG', 'testSendingPicture.JPG')
#client.send_string("string sending test")
#client.cmd_close_server()
client.close_comm()
