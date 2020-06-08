## The Blockchain Implementation

The blockchain functionality is provided by a single class, `BlockChain`, in the `toychain.blockchain` module.
It is a simple list of blocks, each block in the chain consisting of a dictionnary with the following keys:

* the `index` at which it is located in the chain,
* a `timestamp` of when the block was added to the chain,
* the list of `transactions` recorded in the block,
* the `proof` of validity for itself,
* a `previous_hash` tag referencing the hash of the previous block in the chain, for immutability.

## What's in the Blockchain?

The json payload for an example block with a single transaction would look like this:
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

!!! tip "Want to learn a bit about Blockchains?"
    If you want to dive a bit into how cryptocurrencies and blockchains work,
    then watch [this excellent video][3b1b_bitcoin] by 3Blue1Brown.

[3b1b_bitcoin]: https://www.youtube.com/watch?v=bBC-nXj3Ng4