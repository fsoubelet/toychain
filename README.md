<h1 align="center">
  <b>toychain</b>
</h1>

toychain is a very simplistic blockchain node modeling in Python.
While the code is my own adaptation, the implementation is from the very good [tutorial][tutorial_link] by Daniel van Flymen.
This adaptation uses [`FastAPI`][fastapi_link] as a web framework, and [`uvicorn`][uvicorn_link] as ASGI server instead of the `Flask` app from van Flymen's tutorial.

# Running

This repository uses `Poetry` as a build tool.
Get a local copy through VCS and to set yourself up with `poetry install`.

The `poetry run node` command is predefined to start up a node, by default at `localhost:5000`.
Additionally, you can specify the host and port on which to run the node with the `--host` and `--port` flags.
You can then use the same command to spin up several nodes on different ports.

## Docker

It is possible to run nodes as docker containers.
To do so, clone the repository then build the image with `docker build -t blockchain .`

You can then run the container by mapping the node's port to a desired one at `localhost` on your machine.
To map the node to port 5000, run:
```bash
$ docker run --init --rm -p 5000:5000 blockchain
```

To emulate additional nodes, vary the public port number:
```bash
$ docker run --init --rm -p 5001:5000 blockchain
$ docker run --init --rm -p 5002:5000 blockchain
$ docker run --init --rm -p 5003:5000 blockchain
```

You can then play around by POSTing to `/nodes/register` to add all your running instances to one another's networks, POSTing transactions, mining new blocks, and resolving the blockchain.

# Functionality

## The Chain

The blockchain is a simple list of blocks.
A `block` in the chain consists of a dictionnary with the following keys:
- the `index` at which it is located in the chain,
- a `timestamp` of when the block was added to the chain,
- the list of `transactions` recorded in the block,
- the `proof` of validity for itself,
- a `previous_hash` tag referencing the hash of the previous block in the chain, for immutability.

A simple example block (with a single transaction) as a json payload would look like this:
```json
block = {
    "index": 1,
    "timestamp": 1506057125.900785,
    "transactions": [
        {
            "sender": "8527147fe1f5426f9dd545de4b27ee00",
            "recipient": "a77f5cdfa2934df3954a5c7c7da5df1f",
            "amount": 5,
        }
    ],
    "proof": 324984774000,
    "previous_hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

## The Node Implementation

The blockchain functionality is provided by a single class, `BlockChain`, in the `toychain.blockchain` module.
An instance of the `BlockChain` class is used to run a node.
Each node stores a full blockchain, the current transactions (not yet written in the chain), and the list of other nodes in the network.
It can:
- Add a transaction to the list of current transactions,
- Add a new (validated) block to the chain,
- Run the proof of work algorithm (here simple, for the sake of computation time),
- Validate the `proof` of a block,
- Register other nodes on the network,
- Infer an arbitrary node's blockchain's validity,
- Resolve conflict through a consensus algorithm, checking all nodes' chains in the network and adopting the longest valid one.

A node is ran as a REST API using the `FastAPI` web framework, and is attributed a `UUID` at startup.
The implementation is in the `toychain.node` module, and the available endpoints of a node are:
- `GET` endpoint `/mine` to trigger the addition of a new block to the chain,
- `POST` endpoint `/transactions/new` to add a transaction to the node's list,
- `GET` endpoint `/chain` to pull the full chain,
- `POST` endpoint `/nodes/register` to register other nodes' addresses as part of the network,
- `GET` endpoint `/nodes/resolve`: to trigger a run of the consensus algorithm and resolve conflicts: the longest valid chain of all nodes in the network is used as reference, replacing the local one, and is returned.

Once the server is running (for instance with `python -m toychain`), an automatic documentation for those is served at the `/docs` and `/redoc` endpoints.

Let's consider our node is running at `localhost:5000`.
POSTing a transaction to the node's `transactions/new` endpoint with cURL would be done as follows:
```bash
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "d4ee26eee15148ee92c6cd394edd974e",
 "recipient": "someone-other-address",
 "amount": 5
}' "http://localhost:5000/transactions/new"
```

Let's now consider that we have started a second node at `localhost:5000`.
POSTing a payload to register this new node to the first one's network with cURL would be done as follows:
```bash
curl -X POST -H "Content-Type: application/json" -d '{
 "nodes": ["http://127.0.0.1:5001"]
}' "http://localhost:5000/nodes/register"
```

If you would rather use [`httpie`][httpie_link], those commands would be, respectively: 
```bash
echo '{ "sender": "d4ee26eee15148ee92c6cd394edd974e", "recipient": "someone-other-address", "amount": 5 }' | http POST http://localhost:5000/transactions/new
```
```bash
echo '{ "nodes": ["http://127.0.0.1:5001"] }' | http POST http://localhost:5000/nodes/register
```

[fastapi_link]: https://fastapi.tiangolo.com/
[httpie_link]: https://httpie.org/
[tutorial_link]: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
[uvicorn_link]: https://www.uvicorn.org/