# Module 1 - Create a Blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain

class Block:

  def __init__(self, index, proof, previous_hash):
    self.index = index
    self.timestamp = str(datetime.datetime.now())
    self.proof = proof
    self.previous_hash = previous_hash
  # End __init__

  def as_json(self):
    return {
       'index': self.index,
       'timestamp': self.timestamp,
       'proof': self.proof,
       'previous_hash': self.previous_hash
    }
  # End as_json
# End Block


class Blockchain:

  INITIAL_HASH = '0'
  INITIAL_PROOF = 1

  def __init__(self):
    self.chain = []
    self.create_block(proof = self.INITIAL_PROOF, previous_hash = self.INITIAL_HASH)
  # End __init__

  def create_block(self, proof, previous_hash):
    block = Block(len(self.chain) + 1, proof, previous_hash)
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
    # End while

    return True
  # End is_chain_valid

  def as_json(self):
    return {
      'chain': map(lambda block: block.as_json(), self.chain),
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
# End Blockchain

# Part 2 - Mining our Blockchain

## Creating a web app

app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
  last_block = blockchain.get_last_block()
  proof = blockchain.proof_of_work(last_block.proof)
  previous_hash = blockchain.hash(last_block)
  new_block = blockchain.create_block(proof, previous_hash)
  response = new_block.as_json()
  response.update({'messages': 'Congratulations, you just mined a block'})

  return jsonify(response), 200
# End mine_block

@app.route('/get_chain', methods = ['GET'])
def get_chain():
  return jsonify(blockchain.as_json(), 200)
# End get_chain

@app.route('/is_valid_chain', methods = ['GET'])
def is_valid_chain():
  return jsonify(blockchain.is_chain_valid(blockchain.chain), 200)

# app.run('0.0.0.0', 5000)