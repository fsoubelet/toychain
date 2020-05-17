"""
Node runner for Blockchain, to interact with using HTTP requests.
"""

from typing import List
from uuid import uuid4

from flask import Flask, jsonify
from loguru import logger

from toychain.blockchain import BlockChain

logger.info("Instantiating node")
app = Flask(__name__)

logger.info("Generating globally unique address for this node")
node_identifier = str(uuid4()).replace("-", "")

logger.info("Instantiating Blockchain")
blockchain = BlockChain()


@app.route("/mine_block", methods=["GET"])
def mine_block():
    return "We will mine a new Block"


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    return "We will add a new transaction"


@app.route("/chain", methods=["GET"])
def full_chain():
    """
    Returns the full blockchain after a GET request.

    Returns:
        The node's full blockchain list, as a flask Response.
    """
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
