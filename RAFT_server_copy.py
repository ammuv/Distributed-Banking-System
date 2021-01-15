#!/usr/bin/env python3
# Distributed Systems - Amr Fall 2020
# Final Project - Distributed blockchain using Raft

import time
import random
# import socket programming library
import socket
import pickle
import struct

# import thread module
from _thread import *
import threading

#library for sha256
import hashlib

import string
import random

# DEBUG = False
TESTING = False
tested_lines = list(range(38))
for i in range(38):
    tested_lines[i] = i

def print_tested_lines():
    relevant_lines = tested_lines.copy()
    # relevant_indices = [0, 4, 15, 19, 23, 24, 25, 27, 28, 29, 33, 34, 35]
    #relevant_indices = [19, 25, 27, 28, 34, 35, 37]
    relevant_indices = []
    for i in range(37, -1, -1):
        if i not in relevant_indices:
            relevant_lines.pop(i)
    print(relevant_lines)

'''
Files:

 message_passing_server:
     Pass messages from one RAFT server to another

 Raft_server:
     Main file
'''

'''
Steps to build the Project:

    ##############################################################################################

    1. Implement blockchain:
       User must be able to insert data while hash computation happens parallely
       Testing:
           1. insert data
           2. output hash table at each point
           3. output operations as they happen to ensure proper order

    2. Set up message passing server (details written in that file) - First implement sketch there
       2 and 3 are intertwined so might need to implement classes in 3 before 2!

    #Note: Pickle necessary in this project since writing classes for messages is easier 

    3. Implement RAFT without leader election (we fix a leader for now and do all operations)
       Testing:
           1. insert data in blockchain at the fixed leader server
           2. Ensure once block inserted in blockchain we pass this message to other RAFT server.

    4. Add leader election to RAFT - implement component in message passing server also
       Testing:
           1. check if leader election happens properly and a leader is elected.
    
    5. Add network Failure
           1. This component needs to be implemented in message passing server
           2. Do testing to ensure failure works

'''

'''
Components:

 List of Clients and Client balance table (on disk):

 Locks - for blockchain 

 Blockchain (log):

 ####
     ### For later: Need to write blockchain into disk
     
     class Blockchain{
     
        ###

        Data members:

        ###
         
        1. current_hash - hash of last block inserted in the blockchain

        2. list_current_block - block not yet inserted into blockchain

        3. list_blockchain - blockchain stored as a array

        #########################################################################################################################

        Member functions:

        ####

        1. find_hash_head_current_block

                * needs to be a threaded function running parallely,
                i.e user should be allowed to enter new data even when this is happening.

                * but user insert - have higher precedence (look up how to give more power to threads)

                * Once hash is found - remove head element and call insert block into block chain as a thread

                * return if the list_current_block is empty
                                  
                                  
        2. insert_block_blockchain( hash value, block ) - modify current_hash and insert the block into blockchain

        
        3. insert_data - insert user data to last block on list_current_block or if full add an extra block

        4. clear_list_current_block - clear everything in the current_block.
        
     }

     class RAFT_message{

     }

'''
# Global variables
port_ids = [13000, 13001, 13002]
tau = 0.02 #delay random variable

# necessary Locks 
blockchain_lock = threading.Lock()
print_lock = threading.Lock()
my_id = 1

def print_with_lock(*msg):
    with print_lock:
        print(*msg)

# Use this instead of calling input() directly.
def input_with_lock(msg):
    with print_lock:
        return input(msg)

def print_usernames():
    for i in range(len(port_ids)):
        print(str(i) + ": " + str(port_ids[i]))

def get_user_num(num_users):
    while True:
        user_num = int(input("Enter a server number: "))
        if 0 <= user_num and user_num < num_users:
            return int(user_num)
        else:
            print_with_lock("Invalid entry.")

class Block:
    def __init__(self):
        self.term = 0
        self.hash_val = "dummyhash"
        self.nonce = "dummynonce"
        self.transactions = []

    def print_str(self):
        return "Term: " + str(self.term) + ", " + "Hash: " + str(self.hash_val) + ", " + "Nonce: " + str(self.nonce)+ ", " + "Transactions: " + str(self.transactions)
    
    def print(self):
        print_with_lock("Term: " + str(self.term) + ", " + "Hash: " + str(self.hash_val) + ", " + "Nonce: " + str(self.nonce)+ ", " + "Transactions: " + str(self.transactions))
    
class Blockchain:
    def __init__(self):
        self.block_chain = []
        self.current_blocks = []
        self.current_hash = -1
        
    def find_hash_head_current_block(self): #call as thread
        while True:
            if len(self.current_blocks)!=0:
                while len(self.current_blocks)!=0:
                    
                    blockchain_lock.acquire()
                    
                    #generate nonce randomly here
                    res = ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k = 6))  #6 length random string
                    nonce = str(res)
                    hash_string = str(self.current_blocks[0].transactions) + nonce 
                    result = hashlib.sha256(hash_string.encode())
                    result = result.hexdigest()
                    
                    if result[len(result)-1] == '0' or result[len(result)-1] == '1' or result[len(result)-1] == '2':
                        self.current_blocks[0].nonce = nonce
                        self.current_blocks[0].hash_val = self.current_hash
                        self.current_hash = result
                        self.block_chain.append(self.current_blocks[0])
                        self.current_blocks.pop(0)

                        print_with_lock("\nNonce successful \n")
                        print_with_lock("Block_chain:")
                        for i in range(len(self.block_chain)):
                            self.block_chain[i].print()
                        print_with_lock("Current_blocks:")
                        for i in range(len(self.current_blocks)):
                            self.current_blocks[i].print()
                        
                    blockchain_lock.release()
                        
                    time.sleep(0.01)
            else:
                time.sleep(0.01)

    def compute_prev_hash(self):
        if len(self.block_chain)!=0:
            size = len(self.block_chain)
            hash_string = str(self.block_chain[size-1].transactions) + self.block_chain[size-1].nonce 
            result = hashlib.sha256(hash_string.encode())
            self.current_hash = result.hexdigest()
            tested_lines[0] = [0, True]
        else:
            self.current_hash = -1
            tested_lines[1] = [1, True]

    def search_data(self,data):
        with blockchain_lock:
            size = len(self.current_blocks)
            for i in range(size-1,-1,-1):
                for j in range(len(self.current_blocks[i].transactions)-1,-1,-1):
                    tran = self.current_blocks[i].transactions[j]
                    if tran[1]==data[1] and tran[0]==data[0]:
                        return True
                    if tran[1]==data[1] and tran[0]<data[0]:
                        return False

            size = len(self.block_chain)
            for i in range(size-1,-1,-1):
                for j in range(len(self.block_chain[i].transactions)-1,-1,-1):
                    tran = self.block_chain[i].transactions[j]
                    if tran[1]==data[1] and tran[0]==data[0]:
                        return True
                    if tran[1]==data[1] and tran[0]<data[0]:
                        return False

            return False
            
        
    def insert_data(self,data,term):

        if self.search_data(data)==True:
            return
            
        blockchain_lock.acquire()
        #insert data into block list
        size = len(self.current_blocks)
        
        if size == 0 or len(self.current_blocks[size-1].transactions) == 3:
            block = Block()
            block.term = term
            #block.transactions = []
            block.transactions.append(data)
            self.current_blocks.append(block)
            tested_lines[2] = [2, True]
        else:
            self.current_blocks[size-1].transactions.append(data)
            tested_lines[3] = [3, True]
            
        print_with_lock("\nData written into new block \n")

        print_with_lock("Block_chain:")
        for i in range(len(self.block_chain)):
            self.block_chain[i].print()

        print_with_lock("Current_blocks: ")    
        for i in range(len(self.current_blocks)):
            self.current_blocks[i].print()
        
        blockchain_lock.release()

    def clear_current_block_list(self):
        self.current_blocks.clear()

    def start_thread_for_nonce(self):
        start_new_thread(self.find_hash_head_current_block,())

    def print(self):
        print_with_lock("Block Chain:")
        for i in range(len(self.block_chain)):
            self.block_chain[i].print()
        #print("Previous Hash:", self.current_hash)

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

    def __init__(self, candidateId, term, lastLogIndex, lastLogTerm):
        self.msg_type = "RequestVoteRPC"
        self.candidateId = candidateId
        self.term = term
        self.lastLogIndex = lastLogIndex
        self.lastLogTerm = lastLogTerm
        
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

    def print(self):
        print_with_lock("msg_type: " + self.msg_type)
        print_with_lock("term: " + str(self.term))
        for entry in self.entries:
            entry.print()
        
class AppendEntriesRPCReply:
    def __init__(self):
        self.msg_type = "AppendEntriesRPCReply"
        self.req = None # contain the RPC to which it replied
        self.term = -1
        self.success = False
    
    def print(self):
        if self.req is None:
            print_with_lock("None")
        else:
            self.req.print()
    
class Raft:
             
            
    def __init__(self, s):
        self.s = s # message passing server

        #reading from file
        from_file = True

        if from_file:
            file_name = 'persistent_state'+str(my_id) # file name that persistent state is stored in
            f = open(file_name, 'rb')   # 'rb' for reading binary file
            persistent_state = pickle.load(f)     # file stored using pickle so we need to load data
            f.close()
            
            self.starting_from_disk(persistent_state["current_term"],persistent_state["voted_for"],
                               persistent_state["block_chain"])
            tested_lines[4] = [4, True]
        else:
            self.starting_from_disk(0,-1,Blockchain())
            tested_lines[5] = [5, True]


        self.election_restart = True
        self.commit_index = -1 #index upto which blockchain has been committed
        self.balance = {"A": 1000, "B": 1000, "C": 1000} # dictionary maintaining balance of clients
        
        self.next_index = {}
        self.leader = -1
        self.list_msg = []

        self.blockchain.start_thread_for_nonce()
        start_new_thread(self.election_timer, ())

        start_new_thread(self.handle_msgs, ())
        start_new_thread(self.thread_listen_server, (self.s,))
        start_new_thread(self.write_disk, ())
        
    def starting_from_disk(self,current_term,voted_for,block_chain):
        # In disk we just store the current_term, voted_for, block_chain

        # If starting for first time, current_term = 0, voted_for = -1, block_chain = Blockchain()
        # and can be called from __init__ - constructor
        
        self.current_term = current_term
        self.voted_for = voted_for
        if voted_for == my_id:
            self.role = "candidate" #when you crashed, you voted for yourself so must have been candidate
        else:
            self.role = "follower" #after starting from crash, start as follower
        self.blockchain = block_chain
        self.blockchain.current_blocks = []

        print_with_lock("Started with Persistent Values:")
        print_with_lock("TERM:",self.current_term,", VOTED FOR:", self.voted_for)
        self.blockchain.print()

        #all other initialization same as init

    def write_disk(self):
        ''' Function to write persistent state to disk
        '''
        print_with_lock("Function write to disk entered")
        file_name = 'persistent_state'+str(my_id)# file name to store persistent state
        
        while True:
            print_with_lock("Started disk write")
            f = open(file_name, 'wb')   # 'wb' instead 'w' for binary file
            with blockchain_lock: #persistent state stored as dict
                data = {"current_term":self.current_term,"voted_for":self.voted_for,"block_chain":self.blockchain}
            pickle.dump(data,f,-1)       # -1 specifies highest binary protocol
            f.close()
            print_with_lock("Finished writing to disk")
            time.sleep(20)                         

    def send_server(self,msg): #msg is a pickled msg
        time.sleep(tau*random.randint(1,6))
        serialized_data = msg
        self.s.send(struct.pack('>I', len(serialized_data)) + serialized_data)
        
    def thread_listen_server(self, s):
        print_with_lock("starting listen")
         
        while True:
            data_size = struct.unpack('>I', s.recv(4))[0]
            received_payload = b""
            remaining_payload_size = data_size
            while remaining_payload_size != 0:
                received_payload += s.recv(remaining_payload_size)
                remaining_payload_size = data_size - len(received_payload)
                tested_lines[6] = [6, True]
            msg = pickle.loads(received_payload)
            self.list_msg.append(msg)
            time.sleep(0.001)
        # close the connection
        s.close()

    def handle_msgs(self):
        while True:
            if len(self.list_msg)==0:
                continue
            else:
                msg = self.list_msg[0]
                self.list_msg.pop(0)
                msg_type = msg["msg"].msg_type
                tested_lines[7] = [7, True]
            #print("type", msg_type)
                if msg_type == "ForwardClientData":
                    print_with_lock("Received CLIENT request:", msg["msg"].data)
                    self.recv_data(msg["msg"])
                    tested_lines[8] = [8, True]
                elif msg_type == "RequestVoteRPC":
                    reply = self.reply_to_RequestVoteRPC(msg["msg"])
                    msg = pickle.dumps({"from": my_id, "to": msg["from"], "msg": reply})
                    self.send_server(msg)
                    print_with_lock("Sent VOTE REPLY")
                    tested_lines[9] = [9, True]
                elif msg_type == "RequestVoteRPCReply":
                    self.recv_reply_to_VoteRPC(msg["msg"])
                    tested_lines[10] = [10, True]
                elif msg_type == "AppendEntriesRPC":
                    reply = self.reply_to_AppendEntriesRPC(msg["msg"])
                    if reply is not None:
                        msg = pickle.dumps({"from": my_id, "to": msg["from"], "msg": reply})
                        self.send_server(msg)
                        tested_lines[11] = [11, True]
                else: # "AppendEntriesRPCReply"
                    self.recv_reply_to_AppendEntryRPC(msg)
                    tested_lines[12] = [12, True]
                time.sleep(0.02)

    def election_timer(self): #election timer that will run as thread 
        
        self.election_restart = False
        sleep_time = random.randint(20,45)
        #print("Restarting election timer")
        for timer in range(sleep_time): #election time out when timer reaches 100
            time.sleep(1)
            if self.election_restart == True: #election will be restarted 
                start_new_thread(self.election_timer,())
                tested_lines[13] = [13, True]
                return
        # TODO: check candidate function
        if self.role == "follower" or self.role == "candidate":
            self.role = "candidate"
            self.candidate_function()
            tested_lines[14] = [14, True]
        
        start_new_thread(self.election_timer,())
        
    def is_log_complete(self,index,term):
        '''
            This function checks if the current log is better than
            another log given last index and term of the other log.

            Return: True if other log is better else False
        '''
        with blockchain_lock:
            size = len(self.blockchain.block_chain)

            if size == 0: #nothing in blockchain case
                return True

            if self.blockchain.block_chain[size-1].term < term or (self.blockchain.block_chain[size-1].term == term and size-1<=index):
                tested_lines[15] = [15, True]
                return True

            return False
            
    def reply_to_RequestVoteRPC(self, req): # RequestVoteRPC req
        '''
        This function responds to the Request Vote RPC that it gets according to RAFT.
        Input: RequestVoteRPC object req
        Output: RequestVoteRPCReply object reply
        '''
        #need to modify later with locks diskwrite etc..
        print_with_lock("Received Request for VOTE from", req.candidateId)
        
        if req.term > self.current_term:
            self.current_term = req.term
            #if self.role != "follower": #step down if leader or candidate
            self.role = "follower"
            self.follower_function()
            tested_lines[16] = [16, True]
                
        if ( req.term == self.current_term and (self.voted_for == -1 or self.voted_for == req.candidateId) and 
                self.is_log_complete(req.lastLogIndex,req.lastLogTerm) ):
            #print("INSIDE IF")
            #print("lastLogIndex:", req.lastLogIndex)
            #print("lastLogTerm:", req.lastLogTerm)
            self.voted_for = req.candidateId # vote for the candidate
            self.election_restart = True #reset election time_out
            tested_lines[17] = [17, True]

        reply = RequestVoteRPCReply()
        reply.term = self.current_term
        reply.req = req

        if self.voted_for == req.candidateId:
            reply.voteGranted = True
            print_with_lock("VOTE Granted")

        return reply

    def recv_reply_to_VoteRPC(self, reply): # RequestVoteRPCReply req
        print_with_lock("Received VOTE Reply")
        if (self.role == "candidate" and reply.voteGranted and 
                self.current_term == reply.req.term):
            self.role = "leader"
            self.leader_function()
            tested_lines[18] = [18, True]
        elif (self.current_term < reply.term):
            self.current_term = reply.term
            self.role = "follower" #step down and become follower
            self.follower_function()
            tested_lines[19] = [19, True]
            
        #elif (self.role != "follower" and self.current_term < reply.term):
                       

    def commit_entries(self,upto_index):
        '''Starting from commit_index+1, we commit all entries upto index upto_index
        '''
        start = self.commit_index + 1
        for i in range(start,upto_index+1):
            #each transaction will be a list of size either 3 (transfer) or 1 (balance)
            for tran in self.blockchain.block_chain[i].transactions:
                if len(tran) == 4: #tranfer transaction [ from to amount ]
                    if self.balance[tran[1]] >= tran[3]:
                        self.balance[tran[1]] -= tran[3]
                        self.balance[tran[2]] += tran[3]
                        reply = "Transaction: " + str(tran)+ " SUCCESS!"
                        #print_with_lock(reply) # TODO maybe print only if leader?
                        tested_lines[20] = [20, True]
                    else:
                        reply = "INCORRECT: Insufficient Balance for Transaction" + str(tran)
                        #print_with_lock(reply)
                else: #balance transaction
                    reply = "BALANCE for " + str(tran) + ": " + str(self.balance[tran[1]])
                    #print_with_lock(reply)
                    tested_lines[21] = [21, True]
                if self.role == "leader":
                    msg = []
                    msg.append(tran[0])
                    msg.append(reply)
                    msg1 = pickle.dumps({"from": my_id, "to": tran[1], "msg": msg}) #send reply commit to client
                    self.send_server(msg1)
                    tested_lines[22] = [22, True]
                    
            self.commit_index = i
            
        if start<=upto_index:
            self.blockchain.print()
            print_with_lock("\nBalance Table:")
            print_with_lock(self.balance)
            if TESTING:
                print_tested_lines()             
            
    def reply_to_AppendEntriesRPC(self, req): # AppendEntriesRPC req
        '''
        This function responds to the Append Entrie RPC that it gets according to RAFT.
        Input: AppendEntriesRPC object req
        Output: AppendEntriesRPCReply object reply
        '''
        #print("start reply_to_AppendEntriesRPC")
        if len(req.entries) != 0 and TESTING:
            print_tested_lines()

        reply = AppendEntriesRPCReply()
        reply.req = req

        # print("req.term", req.term) 
        # print("curr", self.current_term)
        if req.term < self.current_term or (req.term == self.current_term and self.role == "leader"):
            #print("Hearbeat Ter LESS THAN CURRENT")
            reply.term = self.current_term
            tested_lines[23] = [23, True]
            return reply
        
        #print("TERMS:", req.term, self.current_term)

        if req.term > self.current_term:
            self.current_term = req.term # modify current term
            #if self.role != "follower": # become follower ---> maybe no need of this condition?
                #self.role = "follower"
                #self.follower_function()
            self.role = "follower"
            #print("BECOME FOLLOWER")
            self.follower_function()
            tested_lines[24] = [24, True]

        self.election_restart = True #reset election time_out
        
        reply.term = self.current_term
        self.leader = req.leaderId       

        with blockchain_lock:
            size = len(self.blockchain.block_chain)
            #print("prevlogidx:",req.prevLogIndex,"size:", size)

            if req.prevLogIndex >= size:
                #print("FAILURE REPLY 1")
                return reply #failure reply
            elif (req.prevLogIndex != -1 and
                    self.blockchain.block_chain[req.prevLogIndex].term != req.prevLogTerm): #if prevlogInd exists terms should match
                # print(req.prevLogIndex) # TODO: remove print
                # print(req.prevLogTerm)
                tested_lines[25] = [25, True]
                #print("FAILURE REPLY 2")
                return reply #failure reply

            ind = req.prevLogIndex + 1
            is_mismatch = False
            for i in range(len(req.entries)):# populate block_chain with received entries
                if ind+i >= len(self.blockchain.block_chain):
                    self.blockchain.block_chain.append(req.entries[i])
                    tested_lines[26] = [26, True]
                elif is_mismatch:
                    self.blockchain.block_chain[ind+i] = req.entries[i]
                    tested_lines[27] = [27, True]
                elif (not is_mismatch) and self.blockchain.block_chain[ind+i].term != req.entries[i].term:
                    is_mismatch = True
                    self.blockchain.block_chain[ind+i] = req.entries[i]
                    tested_lines[28] = [28, True]

            size = len(self.blockchain.block_chain) 
            del self.blockchain.block_chain[ind+len(req.entries):size] #delete all extra elements after copying upto consistent index

        self.commit_entries(req.commitIndex)
        
        reply.success = True
        return reply

    def follower_function(self):
        self.voted_for = -1
        self.election_restart = True
    
    def candidate_function(self):
        self.current_term += 1
        
        print_with_lock("\nCANDIDATE with TERM",self.current_term)
        #self.blockchain.print()
        print_with_lock("Balance Table:")
        print_with_lock(self.balance)
        
        self.voted_for = my_id
        self.election_restart = True
        #start_new_thread(self.election_timer,())
        with blockchain_lock:
            size = len(self.blockchain.block_chain)
            #my_id - candidateId, term - current_term, lastLogIndex = size-1, lastLogTerm = term at that index in blockchain
            term = -1
            if size>0:
                term = self.blockchain.block_chain[size-1].term
                tested_lines[29] = [29, True]

            req = RequestVoteRPC(my_id,self.current_term,size-1,term)

        #here, send this request to all other RAFT servers
        for id in port_ids:
            if id == my_id:
                continue
            msg = pickle.dumps({"from": my_id, "to": id, "msg": req})
            self.send_server(msg)
        print_with_lock("Sent vote requests!")

    def send_append_entries_RPC(self, id):
        while self.role == "leader":
            # if DEBUG: 
            #     print("NEW ITER")
            with blockchain_lock:
                size = len(self.blockchain.block_chain) - 1
                if self.next_index[id] <= -1:
                    self.next_index[id] = 0
                    #print_with_lock("LESS THAN") # TODO
                elif self.next_index[id] > size + 1:
                    self.next_index[id] = size + 1 
                    #print_with_lock("GREATER THAN")# TODO
                # if DEBUG: 
                #     print("HERE!!")
                #     print("length of BC:", len(self.blockchain.block_chain))
                #     print("BLOCKCHAIN:", self.blockchain.block_chain)
                # if size >= self.next_index[id]: # TODO: fix this
                req = AppendEntriesRPC()
                req.term = self.current_term
                req.leaderId = my_id
                req.prevLogIndex = self.next_index[id] - 1
                if req.prevLogIndex != -1:
                    req.prevLogTerm = self.blockchain.block_chain[req.prevLogIndex].term
                    tested_lines[37] = [37, True]

                for i in range(self.next_index[id], size + 1):
                    block = self.blockchain.block_chain[i]
                    req.entries.append(block)

                req.commitIndex = self.commit_index
                msg = pickle.dumps({"from": my_id, "to": id, "msg": req})

                if self.role != "leader":
                    return
                self.send_server(msg)

                time.sleep(0.1)

    def leader_function(self):

        # Initialize next_index for each follower
        # start send_append_entries_RPC thread that sends appendentryRPCs (heart beats included)
        print_with_lock("\n!!! Elected LEADER !!! with Term",self.current_term)
        self.blockchain.print()
        print_with_lock("Balance Table:")
        print_with_lock(self.balance)
        with blockchain_lock:
            size = len(self.blockchain.block_chain)
            self.blockchain.compute_prev_hash()
        msg = pickle.dumps({"from": my_id, "to": 12345, "msg": "leader"})
        self.send_server(msg)

        for id in port_ids:
            if id == my_id:
                continue
            self.next_index[id] = size
            start_new_thread(self.send_append_entries_RPC, (id,)) #for both hearbeat and append entries

    def recv_data(self,client_data):
        '''
            Input: ClientData object
            Function: insert this data into blockchain if leader
        '''
        if self.role == "leader":
            self.blockchain.insert_data(client_data.data,self.current_term)
            tested_lines[32] = [32, True]
        elif self.role == "follower" and self.leader != -1:
            msg = pickle.dumps({"from": my_id, "to": self.leader, "msg": client_data})
            self.send_server(msg)
            tested_lines[33] = [33, True]
        elif self.role == "candidate":
            pass 

    def recv_reply_to_AppendEntryRPC(self, msg):
        #print("entering recv_reply_to_AppendEntryRPC")
        if self.role != "leader":
            return

        if msg["msg"].success == False:
            if msg["msg"].term > self.current_term:
                self.current_term = msg["msg"].term
                self.role = "follower" # TODO: check
                self.follower_function()
                tested_lines[34] = [34, True]
            else:
                if (self.next_index[msg["from"]] == msg["msg"].req.prevLogIndex+1 and 
                        self.next_index[msg["from"]] != 0):
                    self.next_index[msg["from"]] -= 1
                    tested_lines[35] = [35, True]
        else:
            if len(msg["msg"].req.entries)>0:
                self.next_index[msg["from"]] = 1 + len(msg["msg"].req.entries) + msg["msg"].req.prevLogIndex
                self.commit_entries(len(msg["msg"].req.entries) + msg["msg"].req.prevLogIndex)
                tested_lines[36] = [36, True]

def main():
    global my_id
    if TESTING:
        print_tested_lines()

    # start up server
    host = "127.0.0.1"
    print_usernames()
    my_id = port_ids[get_user_num(len(port_ids))]

    # connect to message passing server
    host = "127.0.0.1"
    server_port = 12345
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host, server_port))
    serialized_data = pickle.dumps({"from": my_id, "type": "Raft Server"})
    s.send(struct.pack('>I', len(serialized_data)) + serialized_data)

    #print_with_lock('CALLING RAFT')
    raft = Raft(s)
    if TESTING:
        print_tested_lines()
    # start_new_thread(raft.thread_listen_server, (s,)) # TODO put in main function

    while (True):
        pass

if __name__ == "__main__":
    main()
        
 
