# How to run

## Set up 3 Servers on the blockchain network (foo, bar, baz)

CONFIG_FILE=./config/foo.py FLASK_APP=Seancoin.py flask run --port 5001
CONFIG_FILE=./config/bar.py FLASK_APP=Seancoin.py flask run --port 5002
CONFIG_FILE=./config/baz.py FLASK_APP=Seancoin.py flask run --port 5003

## Add nodes to each server so they have knowledge of each other

http://127.0.0.1:5001/connect_node [POST]

{
    "nodes": [
        "http://127.0.0.1:5002",
        "http://127.0.0.1:5003"
    ]
}

http://127.0.0.1:5002/connect_node [POST]

{
    "nodes": [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5003"
    ]
}

http://127.0.0.1:5003/connect_node [POST]

{
    "nodes": [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002"
    ]
}

## Mine a block in one of the nodes

http://127.0.0.1:5001/mine_block [GET]

## Replace chain in other blocks !!!! ERROR Here ATM !!!!

http://127.0.0.1:5002/replace_chain [GET]
http://127.0.0.1:5003/replace_chain [GET]

