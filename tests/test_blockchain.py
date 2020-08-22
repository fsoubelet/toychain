import hashlib

import pytest

from toychain.blockchain import Block, BlockChain, Transaction


class TestNodes:
    @pytest.mark.parametrize(
        "node_address", ["http://192.168.0.1:5000", "http://127.0.0.5:5050", "http://0.0.0.0:8000"]
    )
    def test_register_valid_nodes(self, node_address):
        blockchain = BlockChain()
        blockchain.register_node(node_address)
        assert node_address.split("//")[1] in blockchain.nodes

    @pytest.mark.parametrize("node_adress", ["http//192.168.0.1:5000", "http//127.0.0.5:5050"])
    def test_register_malformed_nodes(self, node_adress):
        blockchain = BlockChain()
        blockchain.register_node(node_adress)
        assert node_adress.split("//")[1] not in blockchain.nodes

    @pytest.mark.parametrize(
        "node_address", ["http://192.168.0.1:5000", "http://127.0.0.5:5050", "http://0.0.0.0:8000"]
    )
    def test_idempotency(self, node_address):
        blockchain = BlockChain()
        for _ in range(5):
            blockchain.register_node(node_address)
        assert len(blockchain.nodes) == 1


class TestBlocksAndTransactions:
    @pytest.mark.parametrize("new_block_proof", list(range(5)))
    @pytest.mark.parametrize("new_block_previous_hash", ["abc", "wow", "much hash", "very valid"])
    def test_block_creation(self, new_block_proof, new_block_previous_hash):
        blockchain = BlockChain()
        latest_block: Block = blockchain.add_block(
            previous_hash=new_block_previous_hash, proof=new_block_proof
        )

        assert len(blockchain.chain) == 2
        assert latest_block.index == 2
        assert latest_block.timestamp is not None
        assert latest_block.proof == new_block_proof
        assert latest_block.previous_hash == new_block_previous_hash

    @pytest.mark.parametrize("sender", ["a", "b", "me", "you"])
    @pytest.mark.parametrize("recipient", ["him", "her", "random_node", "wikipedia"])
    @pytest.mark.parametrize("amount", list(range(5)))
    def test_create_transactions(self, sender, recipient, amount):
        blockchain = BlockChain()
        blockchain.add_transaction(sender=sender, recipient=recipient, amount=amount)
        added_transaction: Transaction = blockchain.current_transactions[-1]

        assert added_transaction
        assert added_transaction.sender == sender
        assert added_transaction.recipient == recipient
        assert added_transaction.amount == amount

    @pytest.mark.parametrize("sender", ["a", "b", "me", "you"])
    @pytest.mark.parametrize("recipient", ["him", "her", "random_node", "wikipedia"])
    @pytest.mark.parametrize("amount", list(range(5)))
    def test_add_block_resets_transaction(self, sender, recipient, amount):
        blockchain = BlockChain()
        blockchain.add_transaction(sender=sender, recipient=recipient, amount=amount)

        initial_transactions_length: int = len(blockchain.current_transactions)
        _ = blockchain.add_block()
        current_transactions_length: int = len(blockchain.current_transactions)

        assert initial_transactions_length != current_transactions_length
        assert len(blockchain.chain) == 2

    def test_return_last_block(self):
        blockchain = BlockChain()
        created_block: Block = blockchain.add_block()

        assert len(blockchain.chain) == 2
        assert created_block is blockchain.chain[-1]

    @pytest.mark.parametrize(
        "sender, recipient, amount", [("me", "him", 5), ("you", "her", 10)],
    )
    def test_chain_validation(self, sender, recipient, amount):
        blockchain = BlockChain()
        last_block: Block = blockchain.last_block
        mined_proof: int = blockchain.proof_of_work(last_block.proof)
        blockchain.add_transaction(
            sender=sender, recipient=recipient, amount=amount,
        )
        previous_hash: str = blockchain.hash(last_block)
        _ = blockchain.add_block(previous_hash=previous_hash, proof=mined_proof)
        assert blockchain.validate_chain(blockchain.chain)

    @pytest.mark.parametrize("previous_hash, proof", [("nonsense", 1), ("surely_wrong", 1e6)])
    def test_detects_invalid_hashes_chain(self, previous_hash, proof):
        blockchain = BlockChain()
        _ = blockchain.add_block(previous_hash=previous_hash, proof=proof)
        assert blockchain.validate_chain(blockchain.chain) is False

    @pytest.mark.parametrize("fake_proof", [1e5, 10])
    def test_detects_invalid_proofs_chain(self, fake_proof):
        blockchain = BlockChain()
        last_block: Block = blockchain.last_block
        previous_hash: str = blockchain.hash(last_block)  # needs to pass hash test
        _ = blockchain.add_block(previous_hash=previous_hash, proof=fake_proof)
        assert blockchain.validate_chain(blockchain.chain) is False


class TestHashingAndProofs:
    def test_hash_is_correct(self):
        blockchain = BlockChain()
        new_block: Block = blockchain.add_block()

        new_block_json_dump: bytes = blockchain.last_block.schema_json().encode()
        new_hash = hashlib.sha256(new_block_json_dump).hexdigest()

        assert len(new_hash) == 64
        assert new_hash == blockchain.hash(new_block)
