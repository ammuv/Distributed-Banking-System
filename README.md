# Distributed-Banking-System
A distributed highly available banking system in Python using blockchain and RAFT protocol.

RAFT is an efficient protocol for the distributed log problem.

Distributed log problem: Given several copies of same dataset placed in different physical locations, maintain consistency with read-write operations. 

RAFT Paper: "In Search of an Understandable Consensus Algorithm (Extended Version)" -- https://raft.github.io/raft.pdf

Python 2.7.12 -- No external dependecies.

Instructions to run in terminal: (each instruction in new terminal window)
  
    python message_passing_server.py # will start middle-man server responsible for passing on messages
    python RAFT_server_copy.py # one for each node in the network (min 3 needed)

