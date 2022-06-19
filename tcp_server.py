import socket
import tqdm
import os

#supported commands
CMDSTRING="SENDSTRING"
CMDFILE="SENDFILE"
CMDQUIT="QUIT"
SEPARATOR="###"

class server:
    acceptedAddress=''
    port=50000
    conn=''
    addr=''
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket init
    def __init__ (self, _address, _port):
        self.acceptedAddress=_address
        self.port=_port
        self.socket.bind((self.acceptedAddress, self.port))
    def __init__ (self): #default port and listening to all addresses. UNSAFE.
        self.socket.bind((self.acceptedAddress, self.port))
    def waitOnConnection (self):
        self.socket.listen(1) #make socket ready for incoming connections
    def getCommand (self):
        self.conn, self.addr = self.socket.accept()
        msg=self.conn.recv(1024).decode('utf-8')
        splited=msg.split(SEPARATOR)
        cmd=splited[0]
        arg1=splited[1]
        arg2=splited[2]
        arg3=splited[3]
        return cmd, arg1, arg2, arg3
    def getFile (self, path, chunksAmount, chunkSize): #it will save the file to path
        fileToWrite=open(path, 'wb')
        for it in range (1,chunksAmount):
            line = self.conn.recv(chunkSize)
            while(line):
                fileToWrite.write(line)
                line=self.conn.recv(chunkSize)
        self.conn.close()
        fileToWrite.close()
        return path
    def closeSocket (self):
        self.socket.close()
    def operate (self):
        while(True):
            cmd, arg1, arg2, arg3 = self.getCommand()
            print (cmd)
            if cmd == CMDFILE:
                print("File saved to path: " + self.getFile(arg1, int(arg2), int(arg3)))
            elif cmd == CMDSTRING:
                print("Got string: " + arg1)
            elif cmd == CMDQUIT:
                break #probably should be disabled, but still can be helpful for debugging purposes.
            else:
                pass

#while function operate(): server waits for a message containing command and three arguments.
#currently supported commands:
#file sending (CMDFILE, path to save file on a server, amounts of chunks file is divided into, size of a chunk)
#string sendinf (CMDSTRING, sended string, empty, empty)
#breaking the operate() while loop (CMDQUIT, empty, empty, empty)
#remark: currently it doesn't use any security mechanism. Will add key support later on.
            
server=server()
server.waitOnConnection()
server.operate()
server.closeSocket()
