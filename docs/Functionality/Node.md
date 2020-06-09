## The Node Implementation

A node is ran as a REST API using the [FastAPI] web framework, and is attributed a [UUID][uuid] at startup.

Each node stores a full blockchain, the current transactions (to be written in the next block), and the list of other nodes registered in the network.
Each node's blockchain is a `BlockChain` object from the `toychain.blockchain` module.

A node can:

- Add a transaction to the list of current transactions,
- Add a new block to its chain,
- Run the proof of work algorithm,
- Validate the `proof` of a block,
- Register other nodes on the network,
- Infer an arbitrary node's blockchain's validity,
- Resolve conflict through a consensus algorithm, checking all nodes' chains in the network and adopting the longest valid one.

??? summary "What endpoints are available for those actions?"
    - `GET` endpoint `/mine` to trigger the addition of a new block to the chain,
    - `POST` endpoint `/transactions/new` to add a transaction to the node's list,
    - `GET` endpoint `/chain` to pull the full chain,
    - `POST` endpoint `/nodes/register` to register other nodes' addresses as part of the network,
    - `GET` endpoint `/nodes/resolve`: to trigger a run of the consensus algorithm and resolve conflicts: the longest valid chain of all nodes in the network is used as reference, replacing the local one, and is returned.

??? tip "How do I remember these?"
    Once the server is running, [FastAPI][fastapi] serves an automated documentation at the `/docs` and `/redoc` endpoints.
    So if your node is running at `localhost:5000`, head over to `localhost:5000/docs` for instance. If you
    simply go to `localhost:5000`, you'll get a hint on where to go ;)

## Interacting with a Node

Let's consider our node is running at `localhost:5000`.
Here's how to POST a transaction to the node's `transactions/new` endpoint, with either [cURL] or [HTTPie]:

=== "cURL"
    
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
     "sender": "d4ee26eee15148ee92c6cd394edd974e",
     "recipient": "someone-other-address",
     "amount": 5
    }' "http://localhost:5000/transactions/new"
    ```

=== "HTTPie"
    
    ```bash
    echo '{ "sender": "d4ee26eee15148ee92c6cd394edd974e", "recipient": "someone-other-address", "amount": 5 }' | http POST http://localhost:5000/transactions/new
    ```

Let's now consider that we have started a second node at `localhost:5001`.
POSTing a payload to register this new node to the first one's network would be done as follows:

=== "cURL"
    
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
     "nodes": ["http://127.0.0.1:5001"]
    }' "http://localhost:5000/nodes/register"
    ```

=== "HTTPie"
    
    ```bash
    echo '{ "nodes": ["http://127.0.0.1:5001"] }' | http POST http://localhost:5000/nodes/register
    ```

[cURL]: https://curl.haxx.se/
[FastAPI]: https://fastapi.tiangolo.com/
[HTTPie]: https://httpie.org/
[uuid]: https://en.wikipedia.org/wiki/Universally_unique_identifier