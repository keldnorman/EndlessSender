#!/usr/bin/python3
#----------------------------------------------------------------------------------
# ABOUT
#----------------------------------------------------------------------------------
#
# This script will send infinite amount of data to clients connecting 
# to the given ip and port - A perfect tool for email harvesters, shodan searchers
# or alike robots that likes to harvest data.
#
#----------------------------------------------------------------------------------
__header__ = '''
    _____\\    _______
   /      \\  |      /\\   
  /_______/  |_____/  \\   
 |   \\   /        /   / 
  \\   \\         \\/   /
   \\  /          \__/_
    \\/ ____    /\\
      /  \\    /  \\
     /\\   \\  /   /      Server Simulator v1.0
       \\   \\/   /       
        \\___\\__/        (C)opyleft Keld Norman, 2022
'''
#----------------------------------------------------------------------------------
# IMPORT MODULES
#----------------------------------------------------------------------------------
import os
import sys
import time
import socket
import struct
import os.path
from threading import Thread
from queue import Queue
#----------------------------------------------------------------------------------
# SEND TEXT FROM THIS FILE
#----------------------------------------------------------------------------------
FILENAME         = "text.txt"    # Get text to send from this file
PATHNAME         = "."           # Find file with text here - Do not end with /
#----------------------------------------------------------------------------------
# RUN SERVER ON THIS IP AMD PORT
#----------------------------------------------------------------------------------
LISTEN_ADDR      = "127.0.0.1"   # Listen on this IP address
LISTEN_PORT      = 1060          # Listen on this PORT
#----------------------------------------------------------------------------------
# VARIABLES
#----------------------------------------------------------------------------------
DELAY_MESSAGE    = 1             # Delay between messages in seconds ( can be .2 )
DELAY_CLIENT     = 60            # Delay clients when max clients number is reached
MAX_CLIENTS      = 10            # Max clients in parallel
MAX_CLIENT_QSIZE = 6             # Messages in queue / client
#
HEADER_FORMAT    = struct.Struct('!I')
ARRAY            = []
#----------------------------------------------------------------------------------
# CHECK FILE 
#----------------------------------------------------------------------------------
def find_file(file_path, file_name):
    full_path = file_path + "/" + file_name
    try:
        if not os.path.exists(file_path):
            print ("\n### ERROR: File path " + filepath + " is invalid.\n")
            return False
        elif not os.path.isfile(full_path):
            print ("\n### ERROR: File " + FILENAME + " not found!\n")
            return False
        elif not os.access(full_path, os.R_OK):
            print ("\### ERROR: nFile " + text_file + " cannot be read.\n")
            return False
        else:
     #      print ("\n File " + text_file + " found and can be read.\n")
            return True
    except IOError as ex:
        print ("\n### I/O error({0}): {1}".format(ex.errno, ex.strerror) + "\n")
    except Error as ex:
        print ("\n### Error({0}): {1}".format(ex.errno, ex.strerror) + "\n")
    return False
#----------------------------------------------------------------------------------
# CLASSES
#----------------------------------------------------------------------------------
class _ClientHandler(Thread):
#----------------------------------------------------------------------------------
    def __init__(self, sock, address, server):
        Thread.__init__(self, daemon = True)
        self.sock = sock
        self.address = address
        self.server = server # Reference to server
        self.queue = Queue() # Message queue

    def _send_item(self, data):
        """Send data to client. Blocks thread."""
        self.sock.sendall(HEADER_FORMAT.pack(len(data)))
        self.sock.sendall(data.encode('utf-8'))

    def run(self):
        """Pop data from queue and sent to client."""
        while True:
            try:
                data = self.queue.get()
                self._send_item(data)
            except BrokenPipeError:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(timestamp, 'Client disconnected (broken pipe)')
                self.server.delete_client(self.ident)
            except OSError:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(timestamp, 'Client disconnected (OSError)')
                self.server.delete_client(self.ident)
            except:
                raise
#----------------------------------------------------------------------------------
class StreamServer(Thread):
#----------------------------------------------------------------------------------
    def __init__(self, address):
        Thread.__init__(self, daemon = True)
        self.address = address
        self._clients = dict()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Disconnect clients and remove client threads when leaving context."""
        try: 
            for ident in self._clients.keys():
                self.delete_client(ident)
        except RuntimeError:
            sys.exit(0)

    def queue_item(self, item, data):
        """Push item to every client queue."""
        for ident, client in self._clients.items():
            if client.queue.qsize() >= MAX_CLIENT_QSIZE:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(timestamp, 'Client', client.sock.getsockname(), 'reached maximum qsize')
                self.delete_client(ident)
            client.queue.put(data)

    def get_qsizes(self):
        """Get list of client queue sizes."""
        count_clients = len([client.queue.qsize() for _, client in self._clients.items()])
        if count_clients >= MAX_CLIENTS:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(timestamp, 'Client count reached maximum (', count_clients , ')')
        return count_clients

    def delete_client(self, ident):
        """Close client socket and delete client thread."""
        self._clients[ident].sock.close()
        del self._clients[ident] # Delete only client thread reference (garbage collection?)

    def run(self):
        """Listen for incomming client connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.address)
            sock.listen(4)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(timestamp, 'Listening at', sock.getsockname())
            while True:
                try:
                    # Refuse connections once client limit reached
                    while len(self._clients) >= MAX_CLIENTS:
                        time.sleep(DELAY_CLIENT)
                    client_sock, client_addr = sock.accept()
                    client_sock.shutdown(socket.SHUT_RD)
                    client = _ClientHandler(client_sock, client_addr, self)
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(timestamp, 'Client connected from', client_sock.getsockname())
                    client.start()
                    self._clients[client.ident] = client
                except:
                    # What exceptions to expect?
                    raise
#----------------------------------------------------------------------------------
# Test if already running and port is in use
#----------------------------------------------------------------------------------
a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
location = (LISTEN_ADDR, LISTEN_PORT)
result_of_check = a_socket.connect_ex(location)
if result_of_check == 0:
    print("\n ### ERROR: Failed to start the server (address", LISTEN_ADDR ,"port", LISTEN_PORT ,"in use)\n")
    a_socket.close()
    quit()
a_socket.close()
#----------------------------------------------------------------------------------
# LOAD TEXT FROM FILE IN TO ARRAY
#----------------------------------------------------------------------------------
text_file = PATHNAME + '/' + FILENAME
if not find_file(PATHNAME, FILENAME):
   quit()
with open(text_file,"r") as fp:
   ARRAY = fp.read().splitlines()
#----------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------
if os.isatty(sys.stdin.fileno()):
    os.system('clear') 
    print(__header__)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("\n### Starting the Infinite Text Transmitting Server..\n")
try:
  client_count_now = 0
  client_count_last_time_we_checked = 0

  if __name__ == '__main__':
      MESSAGES_COUNT=len(ARRAY)
      with StreamServer((LISTEN_ADDR, LISTEN_PORT)) as server:
          server.start() # Start server thread
          last_time = time.time()

          while True: 

              try:
                  for item in range(0,MESSAGES_COUNT):

                      try:
                         server.queue_item(item,str(ARRAY[item] +'\n'))
                         time.sleep(DELAY_MESSAGE)
                         if time.time() - last_time > 10.0:
                            last_time = time.time()
                            client_count_now = server.get_qsizes()
                            if client_count_now != client_count_last_time_we_checked:     
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                                print(timestamp, 'Clients connected:', server.get_qsizes(), "of", MAX_CLIENTS) 
                            client_count_last_time_we_checked = client_count_now

                      except KeyboardInterrupt:
                          sys.exit(0)

              except KeyboardInterrupt:
                  sys.exit(0)

except KeyboardInterrupt:
    sys.exit(0)
#----------------------------------------------------------------------------------
# END OF SCRIPT
#----------------------------------------------------------------------------------
