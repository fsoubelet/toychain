"""
Node runner for Blockchain, to interact with using HTTP requests.
"""

from typing import Dict
from uuid import uuid4

from flask import Flask, jsonify, request
from loguru import logger

from toychain.blockchain import BlockChain

logger.info("Instantiating node")
app = Flask(__name__)

logger.info("Generating globally unique address for this node")
node_identifier = str(uuid4()).replace("-", "")
logger.info(f"This is node ID {node_identifier}")

logger.info("Instantiating Blockchain")
blockchain = BlockChain()
logger.success("Blockchain up and running!")


@app.route("/mine", methods=["GET"])
def mine_block():
    """
    Mining endpoint, witch does three things:
        - Calculate the Proof of Work.
        - Reward the miner by adding a transaction granting 1 coin.
        - Forge the new Block by adding it to the chain.

    Returns:
        A flask response.
    """
    logger.info("Mining proof for a new block")
    last_block: Dict = blockchain.last_block
    last_proof: int = last_block["proof"]
    mined_proof: int = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.add_transaction(
        sender="0", recipient=node_identifier, amount=1,
    )

    logger.info("Forging new block and adding it to the chain")
    previous_hash: str = blockchain.hash(last_block)
    block: Dict = blockchain.add_block(previous_hash=previous_hash, proof=mined_proof)

    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }
    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    """
    Receives transaction data from a POST request and add it to the node's blockchain.

    Returns:
        A flask response.
    """
    logger.info("Received POST request for new transaction, getting data")
    values: Dict = request.get_json()
    print(f"\n{values}\n")

    logger.info("Checking that POSTed data contains the appropriate fields")
    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        logger.error("Missing values in POSTed data")
        return "Missing Values", 400

    logger.info("Creating new transaction from POSTed data")
    transaction_index: int = blockchain.add_transaction(
        values["sender"], values["recipient"], values["amount"]
    )

    response = {"message": f"Transaction added to the list of current transactions"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    """
    Returns the full blockchain after a GET request.

    Returns:
        The node's full blockchain list, as a flask Response.
    """
    logger.info("Full chain requested, sending...")
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200


def main():
    """Runs the node"""
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
