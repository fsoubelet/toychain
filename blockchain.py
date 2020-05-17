"""
Simple emulation of a blockchain.
"""

import hashlib
import json
import sys
from time import time
from typing import Dict, List, Optional

from loguru import logger


class BlockChain:
    """Simple class to emulate a blockchain"""

    def __init__(self):
        self.chain: List[Dict] = []
        self.current_transactions = []
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
        logger.debug("Creating new block")
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

    def new_transaction(
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
        logger.debug("Checking proof validity")
        guess = f"{last_proof}{new_proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if guess_hash[:4] == "0000":
            logger.success("Proof is valid")
            return True
        else:
            logger.debug("Proof is invalid")
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
            proof += 1
        logger.success("Successfully mined block proof")
        return proof
