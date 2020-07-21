import time
from multiprocessing import Process

import pytest
import requests
import uvicorn
from fastapi.testclient import TestClient

from toychain.node import node


class TestGETEndpoints:
    """
    Testing GET endpoints. The consensus algorithm is tested in a full run below as it
    requires many other things to happen first in order to be tested.
    """

    def test_root_page(self):
        client = TestClient(node)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "This is a running node. To get a documentation overview of the available "
            "endpoints and their functionality, head over to the '/docs' endpoint (SwaggerUI "
            "style), or the '/redoc' endpoint (ReDoc style)."
        }

    def test_mine_block(self):
        client = TestClient(node)
        response = client.get("/mine")
        assert response.status_code == 200
        assert response.json()["message"] == "New Block Forged"

        # Chain is initialized with 1 block at creation, so adding one puts it at index 2
        assert response.json()["index"] == 2

        # 'transactions' key is a list, should only contain 1 element
        assert isinstance(response.json()["transactions"], list)
        assert response.json()["transactions"][0]["sender"] == "0"
        assert isinstance(response.json()["transactions"][0]["recipient"], str)
        assert response.json()["transactions"][0]["amount"] == 1

        assert isinstance(response.json()["proof"], int)
        assert isinstance(response.json()["previous_hash"], str)

    def test_get_chain(self):
        client = TestClient(node)
        response = client.get("/chain")
        assert response.status_code == 200
        assert isinstance(response.json()["chain"], list)
        assert response.json()["length"] == 2


class TestPOSTEndpoints:
    def test_registering_node(self):
        client = TestClient(node)
        response = client.post("/nodes/register", json={"nodes": ["http://127.0.0.1:5001"]})
        assert response.status_code == 200
        assert response.json()["message"] == "1 new nodes have been successfully added"
        assert isinstance(response.json()["total_nodes"], list)
        assert response.json()["total_nodes"] == ["127.0.0.1:5001"]

    def test_adding_transactions(self):
        client = TestClient(node)
        response = client.post(
            "/transactions/new", json={"sender": "Lea", "recipient": "Mark", "amount": 10}
        )
        assert response.status_code == 200
        # Expecting mined in block at index 2 because no other block explicitly mined so far
        assert (
            response.json()["message"] == "Transaction added to the list of current "
            "transactions and will be mined into the block at index 2"
        )


class TestFullRun:
    """
    Going through all operations in the walkthrough with two active nodes, and making sure all
    goes well. Only here is tested the consensus functionality, which is important.

    Operations in order are (each steps warants a series of assertions):
     - Start up two nodes at 5000 and 5001 (via fixtures),
     - Registering them to each other,
     - Adding a transaction to both (identical content),
     - Mining a block at both,
     - Querying chains,
     - Mining an additional block only at 5001,
     - Running the consensus for both, checking that 5001 doesn't change and that 5000 changes.
    """

    def test_walkthrough(self, _server_5000, _server_5001):
        time.sleep(2)  # Giving time to start up the node fixtures

        # Registering nodes to each other
        registering_at_5000 = requests.post(
            "http://127.0.0.1:5000/nodes/register", json={"nodes": ["http://127.0.0.1:5001"]}
        )
        registering_at_5001 = requests.post(
            "http://127.0.0.1:5001/nodes/register", json={"nodes": ["http://127.0.0.1:5000"]}
        )
        assert registering_at_5000.status_code == registering_at_5001.status_code == 200
        assert (
            registering_at_5000.json()["message"]
            == registering_at_5001.json()["message"]
            == "1 new nodes have been successfully added"
        )
        assert isinstance(registering_at_5000.json()["total_nodes"], list)
        assert isinstance(registering_at_5001.json()["total_nodes"], list)
        assert registering_at_5000.json()["total_nodes"] == ["127.0.0.1:5001"]
        assert registering_at_5001.json()["total_nodes"] == ["127.0.0.1:5000"]

        # Adding transactions - previously tested so only make sure response is 200
        transactions_5000 = requests.post(
            "http://127.0.0.1:5000/transactions/new",
            json={"sender": "Lea", "recipient": "Mark", "amount": 10},
        )
        transactions_5001 = requests.post(
            "http://127.0.0.1:5001/transactions/new",
            json={"sender": "Lea", "recipient": "Mark", "amount": 10},
        )
        assert transactions_5000.status_code == transactions_5001.status_code == 200

        # Mining into block - TAKES TIME - previously tested so only make sure response is 200
        mine_5000 = requests.get("http://127.0.0.1:5000/mine")
        mine_5001 = requests.get("http://127.0.0.1:5001/mine")
        assert mine_5000.status_code == mine_5001.status_code == 200

        # Querying chains
        chain_5000 = requests.get("http://127.0.0.1:5000/chain")
        chain_5001 = requests.get("http://127.0.0.1:5001/chain")
        assert chain_5000.status_code == chain_5001.status_code
        assert chain_5000.json()["length"] == chain_5001.json()["length"] == 2

        # Adding a block to 5001 and not 5000
        re_mine_5001 = requests.get("http://127.0.0.1:5001/mine")
        assert re_mine_5001.status_code == 200

        # Running consensus for 5001 first, should not change as it is 1 block ahead
        consensus_5001 = requests.get("http://127.0.0.1:5001/nodes/resolve")
        assert consensus_5001.status_code == 200
        assert consensus_5001.json()["message"] == "Our chain is authoritative"
        assert isinstance(consensus_5001.json()["chain"], list)

        # Running consensus for 5000 now, should adopt 5001 chain
        consensus_5000 = requests.get("http://127.0.0.1:5000/nodes/resolve")
        assert consensus_5000.status_code == 200
        assert consensus_5000.json()["message"] == "Our chain was replaced"
        assert consensus_5000.json()["new_chain"] == consensus_5001.json()["chain"]


@pytest.fixture(scope="function")
def _server_5000():
    """
    Fixture to start a node at localhost:5000 in a different process for the duration of the
    calling test.
    """
    process = Process(
        target=uvicorn.run, kwargs={"app": node, "host": "127.0.0.1", "port": 5000}, daemon=True,
    )
    process.start()
    yield
    process.kill()


@pytest.fixture(scope="function")
def _server_5001():
    """
    Fixture to start a node at localhost:5001 in a different process for the duration of the
    calling test.
    """
    process = Process(
        target=uvicorn.run, kwargs={"app": node, "host": "127.0.0.1", "port": 5001}, daemon=True,
    )
    process.start()
    yield
    process.kill()
