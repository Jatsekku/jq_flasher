import socket
import os
from tqdm import tqdm
import math

CMDSTRING="SENDSTRING"
CMDFILE="SENDFILE"
CMDQUIT="QUIT"
SEPARATOR="###"

class client:
    serverAddress=''
    port=50000
    buffersize=1024
    socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__ (self, _address, _port):
        self.serverAddress=_address
        self.port=_port
    def __init__ (self, _address):
        self.serverAddress=_address
    def initConnection(self):
        self.socket.connect((self.serverAddress, self.port))
    def buildMsg (self, cmd, arg1, arg2, arg3):
        return cmd+SEPARATOR+arg1+SEPARATOR+arg2+SEPARATOR+arg3
    def sendString(self, string):
        cmd=self.buildMsg(CMDSTRING,string," "," ") #sending payload as arg1
        self.socket.sendall(cmd.encode('utf-8'))
    def sendFile(self, filepath, serverFilename):
        filetosend=open(filepath,'rb') #b is for binary
        filesize=os.path.getsize(filepath)
        chunksAmount=str(math.ceil(filesize/self.buffersize))
        cmd=self.buildMsg(CMDFILE,serverFilename,chunksAmount,str(self.buffersize))
        print(cmd)
        self.socket.sendall(cmd.encode('utf-8'))
        #file sending
        for it in tqdm(range(0, filesize, self.buffersize), desc="sending file"): #tqdm is for progress bar
            buff=filetosend.read(self.buffersize)
            self.socket.sendall(buff)    
    def closeComm(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
    def cmdCloseServer(self):
        cmd=self.buildMsg(CMDQUIT," "," "," ")
        self.socket.sendall(cmd.encode('utf-8'))

#example code:
client=client('192.168.1.16')
client.initConnection()
#after init, send command to a server. Uncomment one.
#client.sendFile('testjpg.JPG', 'testSendingPicture2222.JPG')
#client.sendString("string sending test")
#client.cmdCloseServer()
client.closeComm()
