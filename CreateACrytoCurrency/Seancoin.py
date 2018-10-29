# Module 2 - Create a Blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urlparse import urlparse

# Part 1 - Building a Blockchain

class Block:

  def __init__(self, index, proof, previous_hash, transactions):
    self.index = index
    self.timestamp = str(datetime.datetime.now())
    self.proof = proof
    self.previous_hash = previous_hash
    self.transactions = transactions
  # End __init__

  def as_json(self):
    return {
       'index': self.index,
       'timestamp': self.timestamp,
       'proof': self.proof,
       'previous_hash': self.previous_hash,
       'transactions': map(lambda transaction: transaction.as_json(), self.transactions)
    }
  # End as_json
# End Block

class Transaction:

  def __init__(self, sender, receiver, amount):
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
  # End __init__

  def as_json(self):
    return {
       'sender': self.sender,
       'receiver': self.receiver,
       'amount': self.amount
    }
  # End as_json

# End Transaction

class Node:

  def __init__(self, address):
    self.url = urlparse(address).netloc
  # End __init__

  def as_json(self):
    return { 'url': self.url }
  # End as_json

# End Node

class Blockchain:

  INITIAL_HASH = '0'
  INITIAL_PROOF = 1

  def __init__(self):
    self.chain = []
    self.transactions = []
    self.create_block(proof = self.INITIAL_PROOF, previous_hash = self.INITIAL_HASH)
    self.nodes = set()
  # End __init__

  def create_block(self, proof, previous_hash):
    block = Block(len(self.chain) + 1, proof, previous_hash, self.transactions)
    self.transactions = []
    self.chain.append(block)
    return block
  # End create_block

  def get_last_block(self):
    return self.chain[-1]
  # End get_last_block

  def proof_of_work(self, previous_proof):
    new_proof = 1
    check_proof = False
    while check_proof is False:
      hash_operation = self.hash(new_proof**2 - previous_proof**2)
      if self.valid_hash(hash_operation):
        check_proof = True
      else:
        new_proof += 1
    # End while

    return new_proof
  # End proof_of_work

  def is_chain_valid(self, chain):
    previous_block = chain[0]
    block_index = 1
    while block_index < len(chain):
      block = chain[block_index]
      if block['previous_hash'] != self.hash_block(previous_block):
        return False
      else:
        previous_proof = previous_block['proof']
        proof = block['proof']
        hash_operation = self.hash(proof**2 - previous_proof**2)

        if self.valid_hash(hash_operation):
          return False
        
        previous_block = block
        block_index += 1
      # End if
    # End while

    return True
  # End is_chain_valid

  def as_json(self):
    return {
      'chain': map(lambda block: block.as_json(), self.chain),
      'transactions': map(lambda transaction: transaction.as_json(), self.transactions),
      'nodes': map(lambda node: node.as_json(), self.nodes),
      'length': len(self.chain)
    }
  # End as_json

  def hash(self, code):
    return hashlib.sha256(str(code).encode()).hexdigest()
  # End hash

  def hash_block(self, block):
    encoded_block = json.dumps(block, sort_keys = True).encode()
    return hash(encoded_block)
  # End hash_block

  def valid_hash(self, hash_code):
    return hash_code[:4] == '0000'
  # End valid_hash

  def add_transaction(self, sender, receiver, amount):
    new_transaction = Transaction(sender, receiver, amount)
    self.transactions.append(new_transaction)

    last_block = self.get_last_block()
    return last_block.index + 1
  # End add_transaction

  def add_node(self, address):
    new_node = Node(address)
    self.nodes.add(new_node)
  # End add_node

  def replace_chain(self):
    network = self.nodes
    longest_chain = None
    max_length = len(self.chain)

    for node in network:
      response = requests.get('http://' + node.url + '/get_chain')

      if response.status_code == 200:

        length = response.json()[0]['length']
        chain = response.json()[0]['chain']

        print(length)

        if length > max_length and self.is_chain_valid(chain):
          max_length = length
          longest_chain = chain
        # End if
      # End if

      if longest_chain:
        self.chain = longest_chain
        return True
      # End if
    return False
    # End for
  # End replace_chain

# End Blockchain

# Part 2 - Mining our Blockchain

## Creating a web app

app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
  last_block = blockchain.get_last_block()
  proof = blockchain.proof_of_work(last_block.proof)
  previous_hash = blockchain.hash(last_block)

  blockchain.add_transaction(sender = node_address, receiver = 'Sean', amount = 10)

  new_block = blockchain.create_block(proof, previous_hash)

  response = { 'block': new_block.as_json() }
  response.update({'message': 'Congratulations, you just mined a block'})

  return jsonify(response), 200
# End mine_block

@app.route('/get_chain', methods = ['GET'])
def get_chain():
  return jsonify(blockchain.as_json(), 200)
# End get_chain

@app.route('/is_valid_chain', methods = ['GET'])
def is_valid_chain():
  return jsonify(blockchain.is_chain_valid(blockchain.chain), 200)
# End is_valid_chain

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
  json = request.get_json()
  transaction_keys = ['sender', 'receiver', 'amount']
  if not all (key in json for key in transaction_keys):
    return 'damn', 400
  else:
    index = blockchain.add_transaction(sender = json['sender'], receiver = json['receiver'], amount = json['amount'])
    response = { 'message': 'This transaction will be added to Block ' + index }
    return jsonify(response), 201
# End add_transaction

# Example Post = { "nodes": ['http://127.0.0.1:5001', 'http://127.0.0.1:5002'] }
@app.route('/connect_node', methods = ['POST'])
def connect_node():
  json = request.get_json()
  nodes = json.get('nodes')
  if nodes is None:
    return "no nodes", 401
  # End if

  for node in nodes:
    blockchain.add_node(node)
  # End for

  response = { 'message': 'ALl the nodes are now connected', 'total_nodes': map(lambda node: node.as_json(), blockchain.nodes)}
  return jsonify(response), 201
# End connect_node

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
  is_chain_replaced = blockchain.replace_chain()
  if is_chain_replaced:
    response = jsonify({'message': 'Chain was replaced', 'chain': blockchain.as_json() })
  else:
    response = jsonify({'message': 'Chain was not replaced', 'chain': blockchain.as_json() })
  # End if else
  return response, 200
# End replace_chain
