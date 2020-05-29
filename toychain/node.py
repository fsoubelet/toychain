"""
Node runner for Blockchain, to interact with using HTTP requests.
"""

import argparse
from typing import Dict, List
from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from toychain.blockchain import BlockChain

logger.info("Instantiating node")
node = FastAPI()

logger.info("Generating globally unique address for this node")
node_identifier = str(uuid4()).replace("-", "")
logger.info(f"This is node ID {node_identifier}")

logger.info("Instantiating Blockchain for this node")
blockchain = BlockChain()
logger.success("Blockchain up and running!")


class ActiveNode(BaseModel):
    nodes: List[str]


class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float


@node.get("/")
def root():
    """
    Greet the user and direct to the docs, that will detail the available endpoints.

    Returns:
        A simple text
    """
    return {
        "message": "This is a running node. To get a documentation overview of the available "
        "endpoints and their functionality, head over to the '/docs' endpoint (Swagger"
        "UI style), or the '/redoc' endpoint (ReDoc style)."
    }


@node.get("/mine")
def mine_block():
    """
    Mining endpoint. GETing `/mine` triggers the following actions:\n
        - Calculating the Proof of Work.\n
        - Rewarding the miner (this node) by adding a transaction granting 1 coin.\n
        - Forging the new Block by adding it to the chain.\n

    Returns:
        A JSON response.
    """
    logger.info("Received GET request to add a block, mining proof for a new block")
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

    return {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }


@node.post("/transactions/new")
def new_transaction(posted_transaction: Transaction):
    """
    Receives transaction data from a POST request and add it to the node's blockchain.

    Returns:
        A JSON response.
    """
    logger.info("Received POST request for new transaction")
    logger.info("Creating new transaction from POSTed data")
    transaction_index: int = blockchain.add_transaction(
        sender=posted_transaction.sender,
        recipient=posted_transaction.recipient,
        amount=posted_transaction.amount,
    )

    return {
        "message": "Transaction added to the list of current transactions at "
        f"index {transaction_index}"
    }


@node.post("/nodes/register")
def register_nodes(posted_transaction: ActiveNode):
    """
    Receives new nodes' location from a POST request and register those to this node's network.

    Returns:
        A JSON response.
    """
    logger.info("Received POST request for new nodes registration, getting payload")

    for node in posted_transaction.nodes:
        logger.debug("Registering new node to the network")
        blockchain.register_node(node)

    return {
        "message": f"{len(posted_transaction.nodes)} new nodes have been successfully added",
        "total_nodes": list(blockchain.nodes),
    }


@node.get("/nodes/resolve")
def consensus():
    """
    Run consensus algorithm to resolve conflicts, sends back status (local node's chain changed,
    or not).

    Returns:
        A JSON response.
    """
    logger.info("Received a GET request to resolve conflicts")
    is_replaced = blockchain.resolve_conflicts()

    if is_replaced:
        response = {"message": "Our chain was replaced", "new_chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}
    return response


@node.get("/chain")
def full_chain():
    """
    GETing `/chain` will returns the full blockchain.

    Returns:
        The node's full blockchain list, as a JSON response.
    """
    logger.info("Full chain requested, sending...")
    return {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }


def _parse_arguments():
    """Simply parse the port on which to run."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        default=5000,
        type=int,
        help="The port on which to run a node. Defaults to 5000.",
    )
    parser.add_argument(
        "--host",
        dest="host",
        default="127.0.0.1",
        type=str,
        help="The host on which to run the node. Defaults to '127.0.0.1', knows as 'localhost'.",
    )
    return parser.parse_args()


def run_node():
    """Runs the node"""
    commandline_arguments = _parse_arguments()
    uvicorn.run(node, host=commandline_arguments.host, port=commandline_arguments.port)


if __name__ == "__main__":
    run_node()
