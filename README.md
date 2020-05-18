<h1 align="center">
  <b>toychain</b>
</h1>

toychain is a very simplistic blockchain modeling in Python.
This repository is not my work, it is my adaptation of the very good [tutorial](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46) by Daniel van Flymen.

## Running

This repository used `Poetry` as a build tool.
To run this, get a copy of this repository through VCS and use Poetry to set yourself up:
```bash
git clone ...
cd ...
poetry install
```

A poetry command is defined to get nodes running, simply run `poetry run node`.

## Functionality

### The Chain

The blockchain is a simple list of blocks.
A block in the chain consists of a dictionnary with the following keys:
- the `index` at which it is located in the chain,
- a `timestamp` of when the block was added to the chain,
- the list of `transactions` recorded in the block,
- the `proof` of validity for itself,
- a `previous_hash` tag referencing the hash of the previous block in the chain, for immutability.

A simple example block (with a single transaction) json payload would look like this:
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

### The Node Implementation

The blockchain functionality is provided by a single class, `BlockChain`, in the `toychain.blockchain` module.
An instance of `BlockChain` can is used to run a node.
Each node stores the full blockchain and the current transactions (not yet written in the chain), and can:
- Add a transaction to the list of current transactions,
- Add a new (validated) block to the chain,
- Run the proof of work algorithm (here simple, for the sake of computation time),
- Validate the `proof` of a block,
- Register other nodes on the network,
- Infer an arbitrary node's blockchain's validity,
- Resolve conflict through a consensus algorithm, checking all nodes' chains in the network and adopting the longest valid one.

A node is ran as a REST API endpoint using a `Flask` application, and is attributed a `UUID`.
The implementation is in the `toychain.app` module, and the implemented endpoints of a node are:
- `/mine`, accepting a `GET` request. This triggers the calculation of a valid proof of work, rewards the miner by awarding 1 coin, and adds the forged block to the chain.
- `/transactions/new`, accepting a `POST` request with the contents of a transaction, and adding it to the list of current transactions.
- `/chain`, accepting a `GET` request and returning the entire blockchain as a json payload.

A transaction POSTed to `transactions/new` would look like this:
```bash
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "d4ee26eee15148ee92c6cd394edd974e",
 "recipient": "someone-other-address",
 "amount": 5
}' "http://localhost:5000/transactions/new"
```
