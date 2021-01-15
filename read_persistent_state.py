import pickle

class Block:
    def __init__(self):
        self.term = 0
        self.hash_val = "dummyhash"
        self.nonce = "dummynonce"
        self.transactions = []

    def print_str(self):
        return "Term: " + str(self.term) + ", " + "Hash: " + str(self.hash_val) + ", " + "Nonce: " + str(self.nonce)+ ", " + "Transactions: " + str(self.transactions)
    
    def print(self):
        print("Term: " + str(self.term) + ", " + "Hash: " + str(self.hash_val) + ", " + "Nonce: " + str(self.nonce)+ ", " + "Transactions: " + str(self.transactions))

class Blockchain:
    def __init__(self):
        self.block_chain = []
        self.current_blocks = []
        self.current_hash = -1
        
    def print(self):
        print("Block Chain:")
        for i in range(len(self.block_chain)):
            self.block_chain[i].print()
        print("Previous Hash:", self.current_hash)
        

def read_data(my_id):
    file_name = 'persistent_state'+str(my_id) # file name that persistent state is stored in
    print("\n\n Starting to read from ",'persistent_state'+str(my_id))
    f = open(file_name, 'rb')   # 'rb' for reading binary file
    persistent_state = pickle.load(f)     # file stored using pickle so we need to load data
    print(persistent_state)
    persistent_state["block_chain"].print()
    f.close()

read_data(13000)
read_data(13001)
read_data(13002)


