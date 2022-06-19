import socket
import tqdm
import os

#supported commands
CMDSTRING="SENDSTRING"
CMDFILE="SENDFILE"
CMDQUIT="QUIT"
SEPARATOR="###"

class server:
    def __init__ (self, address, port=50000):
        self.accepted_address=address
        self.port=port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket init
        self.socket.bind((self.accepted_address, self.port))
  
    def wait_on_connection (self):
        self.socket.listen(1) #make socket ready for incoming connections

    def get_command (self):
        self.conn, self.addr = self.socket.accept()
        msg=self.conn.recv(1024).decode('utf-8')
        splitted=msg.split(SEPARATOR)
        cmd=splitted[0]
        arg1=splitted[1]
        arg2=splitted[2]
        arg3=splitted[3]
        return cmd, arg1, arg2, arg3

    def get_data (self, chunk_size):
        self.conn, self.addr = self.socket.accept()
        self.conn.recv(chunk_size)
        self.conn.close()
    
    def get_file (self, path, chunks_amount, chunk_size): #it will save the file to path
        file_to_write=open(path, 'wb')
        for it in range (1,chunks_amount):
            line = self.conn.recv(chunk_size)
            while(line):
                file_to_write.write(line)
                line=self.conn.recv(chunk_size)
        self.conn.close()
        file_to_write.close()
        return path

    def close_socket (self):
        self.socket.close()

    def operate (self):
        while(True):
            cmd, arg1, arg2, arg3 = self.get_command()
            print (cmd)
            if cmd == CMDFILE:
                print("File saved to path: " + self.get_file(arg1, int(arg2), int(arg3)))
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
server.wait_on_connection()
server.operate()
server.close_socket()
