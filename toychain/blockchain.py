"""
Simple emulation of a blockchain.
"""

import hashlib
import json
from time import time
from typing import Dict, List, Optional
from urllib.parse import ParseResult, urlparse

import requests
from loguru import logger


class BlockChain:
    """Simple class to emulate a blockchain"""

    def __init__(self):
        self.chain: List[Dict] = []
        self.current_transactions: List[Dict] = []
        self.nodes = set()
        logger.debug("Initiating first block")
        self.add_block(previous_hash=1, proof=100)

    def add_block(self, previous_hash: Optional[str] = None, proof: int = None) -> Dict:
        """
        Create a new block and add it to the chain.

        Args:
            previous_hash: string (optional), hash of the previous block in the chain.
            proof: integer, the proof given by the proof of work algorithm.

        Returns:
            The new block as a dictionary.
        """
        logger.debug("Creating a new block")
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }

        logger.debug("Resetting the current list of transations")
        self.current_transactions = []

        logger.debug("Adding block to the chain")
        self.chain.append(block)
        return block

    def add_transaction(
        self, sender: str = None, recipient: str = None, amount: float = None
    ) -> int:
        """
        Adds a new transaction to the list of transactions.

        Args:
            sender: string, address of the sender.
            recipient: string, address of the recipient.
            amount: float, the amount of the transaction.

        Returns:
            An integer containing the address of the block that will hold this transaction.
        """
        logger.debug("Adding transaction to the blockchain")
        self.current_transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )
        return self.last_block["index"] + 1

    @property
    def last_block(self) -> Dict:
        """
        Returns the last block in the chain.

        Returns:
            The last block in the chain, as a dictionnary object.
        """
        return self.chain[-1]

    @staticmethod
    def hash(block: Dict = None) -> str:
        """
        Hashes a new block.

        Args:
            block: dictionnary with the block's contents.

        Returns:
            The block's hash.
        """
        logger.debug("Ordering dictionary and dumping to json")  # ordering for consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        logger.debug("Hashing dumped block")
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def validate_proof(last_proof: int = None, new_proof: int = None) -> bool:
        """
        Validates a proof: does hash(last_proof, new_proof) contain 4 leading zeroes?

        Args:
            last_proof: integer, the previous proof in the chain.
            new_proof: integer, the new proof.

        Returns:
            True if new_proof is validated, False otherwise.
        """
        logger.trace("Checking proof validity")
        guess = f"{last_proof}{new_proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if guess_hash[:4] == "0000":
            logger.debug("Proof iteration is valid")
            return True
        else:
            logger.trace("Proof is invalid")
            return False

    def proof_of_work(self, last_proof: int = None) -> int:
        """
        Simple Proof of Work Algorithm:
            - Find a number p' such that hash(pp') has leading 4 zeroes, where p is the previous p'
             - p is the previous proof, and p' is the new proof
        Args:
            last_proof: integer, the previous proof in the chain.

        Returns:
            The new proof, an integer.
        """
        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            logger.trace("Proof didn't pass, iterating")
            proof += 1
        logger.success("Successfully mined block proof")
        return proof

    def register_node(self, address: str = None) -> None:
        """
        Register a new node as part of the network by adding it to the list of nodes.

        Args:
            address: string, address of node to register. Eg. 'http://192.168.0.5:5000'

        Returns:
            Nothing, adds in place.
        """
        logger.debug(f"Parsing new node address {address}")
        parsed_url: ParseResult = urlparse(address)
        node_netloc: str = parsed_url.netloc

        if node_netloc in self.nodes:
            logger.warning(f"Node at {address} is already registered, skipping")

        logger.debug("Adding new element to network's registered nodes")
        self.nodes.add(node_netloc)

    def validate_chain(self, chain: List[Dict]) -> bool:
        """
        Determine if a given blockchain from any arbitrary node in the network is valid.

        Args:
            chain: list, a complete blockchain (list of blocks as dicts).

        Returns:
            True if the chain is valid, False otherwise
        """
        logger.debug("Determining chain validity")
        last_block = chain[0]

        for current_index in range(1, len(chain)):
            logger.trace(f"Inspecting block at index {current_index}")
            inspected_block = chain[current_index]

            logger.trace("Checking block's hash")
            if inspected_block["previous_hash"] != self.hash(last_block):
                logger.error(
                    f"Invalid block tag 'previous_hash' " f"{inspected_block['previous_hash']}"
                )
                return False

            logger.trace("Checking block's proof of work")
            if not self.validate_proof(
                last_proof=last_block["proof"], new_proof=inspected_block["proof"]
            ):
                logger.error(
                    f"Invalid proof from last block's proof {last_block['proof']} and "
                    f"inspected block's proof {inspected_block['proof']}"
                )
                return False

            logger.trace("Moving on to next block")
            last_block = inspected_block

        logger.debug("Chain is valid!")
        return True

    def resolve_conflicts(self) -> bool:
        """
        This is the Consensus Algorithm. It resolves conflicts by replacing the node's chain with
        the longest valid one in the network.

        Returns:
            True if the node's chain was replaced, False otherwise
        """
        neighbouring_nodes = self.nodes
        new_chain = None
        max_length = len(self.chain)  # initialize with this node's length

        logger.debug("Verifying chains from all nodes in the network")
        for node in neighbouring_nodes:
            logger.debug("Querying node for its full chain")
            node_chain_response = requests.get(f"http://{node}/chain")

            if node_chain_response.status_code == 200:
                logger.trace("Full chain received")
                length = node_chain_response.json()["length"]
                chain = node_chain_response.json()["chain"]

                logger.trace("Checking if requested chain is valid and longer than mine")
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            logger.info("Found a valid chain longer than this node's, adopting it now")
            self.chain = new_chain
            return True

        logger.info("No valid chain was longer than this node's")
        return False
