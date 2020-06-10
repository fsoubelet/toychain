from multiprocessing import Process

import pytest
import requests
import uvicorn
from fastapi.testclient import TestClient
from loguru import logger

from toychain.node import node


class TestGETEndpoints:
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
        assert response.json()["length"] == 2  # TODO: figure out why this is not 1


# @pytest.fixture
# def run_server():
#     process = Process(
#         target=uvicorn.run, kwargs={"app": node, "host": "127.0.0.1", "port": 5000,}, daemon=True,
#     )
#     logger.info("Start process here")
#     process.start()
#     yield
#     logger.info("Kill process now")
#     process.kill()  # Cleanup after test


# def test_this(run_server):
#     logger.info("Sending request here")
#     response = requests.get("http://127.0.0.1:5000")
#     assert response.status_code == 200
