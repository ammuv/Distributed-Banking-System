#!/usr/bin/env python3

import time
import random
import socket
import pickle
import struct

from _thread import *
import threading

# import classes.py
tau = 0.02
class ClientData:
    '''
        Message when a follower forwards client data to the leader
        
        ---> todo : look into what we do when data from client to candidate!
    '''
    def __init__(self):
        self.msg_type = "ForwardClientData"
        self.data = []

class RequestVoteRPC:
    def __init__(self):
        self.msg_type = "RequestVoteRPC"
        self.candidateId = -1
        self.term = -1
        self.lastLogIndex = -1
        self.lastLogTerm = -1

class RequestVoteRPCReply:
    def __init__(self):
        self.msg_type = "RequestVoteRPCReply"
        self.term = -1
        self.voteGranted = False
        self.req = None

class AppendEntriesRPC:
    def __init__(self):
        self.msg_type = "AppendEntriesRPC"
        self.term = -1
        self.leaderId = -1
        self.prevLogIndex = -1
        self.prevLogTerm = -1
        self.entries = [] #log entries to be sent
        self.commitIndex = -1

class AppendEntriesRPCReply:
    def __init__(self):
        self.msg_type = "AppendEntriesRPCReply"
        self.req = -1 # contain the RPC to which it replied
        self.term = -1
        self.success = False

class Block:
    def __init__(self):
        self.term = 0
        self.hash_val = "dummyhash"
        self.nonce = "dummynonce"
        self.transactions = []
    
    def print(self):
        print_with_lock("Term: " + str(self.term) + ", " + "Hash: " + str(self.hash_val) + ", " + "Nonce: " + str(self.nonce)+ ", " + "Transactions: " + str(self.transactions))
    
class Blockchain:
    def __init__(self):
        self.block_chain = []
        self.current_blocks = []
        self.current_hash = -1

# Global variables

port_ids = [13000, 13001, 13002]
clients = ["A", "B", "C"]
connected_sockets = {} # dictionary for mapping connected sockets to RAFT servers
map_name_to_socket = {}
request_no = 0
# matrix showing which pairs of clients are connected
working_connections = {
    13000: {13000: True, 13001: True, 13002: True},
    13001: {13000: True, 13001: True, 13002: True},
    13002: {13000: True, 13001: True, 13002: True}
}

# Locks

print_lock = threading.Lock()
leader = 13000

# Classes

class Test:
    name = 'hi'

    def __str__(self):
        return "My name is: " + self.name

# Functions

def print_with_lock(*msg):
    with print_lock:
        print(*msg)

def input_with_lock(msg):
    with print_lock:
        return input(msg)

def send_msg(to,serialized_data): #msg is pickled msg
    if map_name_to_socket.get(to) is not None:
        time.sleep(tau*random.randint(1,6))
        c = map_name_to_socket.get(to)
        if c is not None:
            try:
                c.send(struct.pack('>I', len(serialized_data)) + serialized_data)
            except:
                return
    #print("Message not sent: Destination server does not exist")

def establish_connections(s):
    while True:
        # establish connection with client
        c, addr = s.accept()
        print("Connected to:", addr[0], ":", addr[1])

        # get port number for this client
        data_size = struct.unpack('>I', c.recv(4))[0]
        received_payload = b""
        remaining_payload_size = data_size
        while remaining_payload_size != 0:
            received_payload += c.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)

        data = pickle.loads(received_payload)
        #{from:,type:"client"} or {from:,type:"RaftServer}

        #print("unpickled:", data )

        name = data["from"]
        map_name_to_socket[name] = c
        
        if data["type"]=="Raft Server":
            print_with_lock("Raft Server number:", name)
            start_new_thread(listen_raftserver, (c,name))
        else: #Client
            print_with_lock("Client name:", name)
            start_new_thread(listen_client, (c,name))    
            
    s.close()

def listen_client(c,client_name):
    global leader
    while True:
        try:
            d = c.recv(4)
        except:
            print_with_lock("Client disconnected (empty message)")
            map_name_to_socket[client_name] = None
            break
        
        data_size = struct.unpack('>I', d)[0]
        received_payload = b""
        remaining_payload_size = data_size
        while remaining_payload_size != 0:
            received_payload += c.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)
        
        obj = pickle.loads(received_payload)
        #to_raftserver = map_name_to_socket.get(leader)
        if map_name_to_socket.get(leader) is None:
            #print("Message not sent: Leader server crashed")
            pass
        else:
            #{from:A, to:}
            print_with_lock("Client message sent to",leader)
            send_msg(leader,received_payload)
    c.close()
            
def listen_raftserver(c,port):
    global leader
    while True:
        # data received from client
        try:
            d = c.recv(4)
        
            #if not d:
            #    print("Client disconnected (empty message)")
            #    map_name_to_socket[port] = None
            #    break
            data_size = struct.unpack('>I', d)[0]
            received_payload = b""
            remaining_payload_size = data_size
            while remaining_payload_size != 0:
                received_payload += c.recv(remaining_payload_size)
                remaining_payload_size = data_size - len(received_payload)

        except:
            print_with_lock("Client disconnected (empty message)")
            map_name_to_socket[port] = None
            break
        
        obj = pickle.loads(received_payload)

        if obj["to"]==12345: #obj["msg"]=="leader"
            leader = obj["from"]
            print_with_lock("Leader updated to",leader)
            continue
            
        to_client = map_name_to_socket.get(obj["to"])
        
        #print(obj)
        #print("OBJ", pickle.loads(msg)["msg"])
        if to_client is None:
            #print("Message not sent: Destination server does not exist")
            pass
        if obj["to"] not in clients and not working_connections[obj["from"]][obj["to"]]:
                pass
            #print("Message not sent: Connection to destination server is broken")
        else:
            #serialized_data = pickle.dumps(obj)
            #send_msg(to_client,serialized_data)
            send_msg(obj["to"],received_payload)

    # connection closed
    c.close()

def print_ports():
    for i in range(len(port_ids)):
        print(str(i) + ": " + str(port_ids[i]))


def print_clients():
    for i in range(len(clients)):
        print(str(i) + ": " + str(clients[i]))

def get_client_num(num_users):
    while True:
        user_num = int(input("Enter a client number: "))
        if 0 <= user_num and user_num < num_users:
            return int(user_num)
        else:
            print("Invalid entry.")

def print_working_connections():
    with print_lock:
        print("Adj matrix for partitioning:")
        for port in port_ids:
            print(str(port)+":",working_connections[port])
            
def main():
    global request_no

    host = "127.0.0.1"
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port)) 
    print("Message passing server socket bound to port", port)

    s.listen(5)
    print("Message passing server socket is listening")

    start_new_thread(establish_connections, (s,))
    time.sleep(10)
    #input("Type when you are ready!")

    while (True):
        #ch = input_with_lock("Enter choice: t (transfer) or b (check balance) or p (partitioning): or n (nothing) ")
        #print_with_lock("Adj matrix for partitioning: ", working_connections)
        print_working_connections()
        ch = input("Enter p for partitioning: ")
        
        if (ch == "b"):
            print_with_lock('Checking balance...')
            req = ClientData()
            request_no += 1
            req.data.append(request_no)
            req.data.append("A")
            msg = pickle.dumps({"from": 12345, "to": leader, "msg": req})
            send_msg(leader,msg)
            print("SENT:", msg)
        elif (ch == "t"):
            print('Whom would you like to transfer to?')
            print_clients()
            to_user = clients[get_client_num(len(clients))]
            print('How much would you like to transfer?')
            dollars = int(input_with_lock('Dollars: '))
            cents = int(input_with_lock('Cents: '))
            amt = dollars * 100 + cents
            req = ClientData()
            request_no += 1
            req.data.append(request_no)
            req.data.append("A")
            req.data.append(to_user)
            req.data.append(amt)
            msg = pickle.dumps({"from": 12345, "to": leader, "msg": req})
            send_msg(leader,msg)
        elif (ch=="p"):
            print("Would you like to break/restore a connection?")
            print_ports()
            server1 = int(input("Enter a server number (sender/recipient): "))
            server2 = int(input("Enter another server number (sender/recipient): "))
            port1 = port_ids[server1]
            port2 = port_ids[server2]

        # # toggle this connection
            working_connections[port1][port2] = not working_connections[port1][port2]
            working_connections[port2][port1] = not working_connections[port2][port1]
            
            if working_connections[port1][port2]:
                print("Connection RESTORED")
            else:
                 print("Connection BROKEN")
        else:
            pass
  
if __name__ == "__main__":
    main()
