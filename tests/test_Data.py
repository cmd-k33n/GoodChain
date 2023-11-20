import unittest
from unittest.mock import MagicMock
from Node import Node
from Data import *
from Transaction import Tx, NORMAL, REWARD, REWARD_VALUE
from Signature import generate_keys


class TestPool(unittest.TestCase):
    def setUp(self):
        self.node = Node()
        self.private_key, self.public_key = generate_keys()
        self.public_adress = encode_public_key(self.public_key)

    def test_save_and_load(self):
        tx1 = Tx(10.1, 10.0, 0.1, self.public_key, self.public_key)
        tx1.sign(self.private_key)
        tx2 = Tx(10.1, 10.0, 0.1, self.public_key, self.public_key)
        tx2.sign(self.private_key)
        txr = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                 self.public_key, self.public_key, REWARD)
        txr.sign(self.private_key)
        self.node.pool.add_tx(tx1)
        self.node.pool.add_tx(tx2)
        self.node.pool.add_tx(txr)
        self.node.save_pool()
        loaded_pool = Pool.load(self.node.pool_hash)
        self.assertEqual(loaded_pool.all_txs(), self.node.pool.all_txs())

        # move txs to ledger
        self.node.move_tx_from_pool_to_current_block(tx1.hash.hex())
        self.node.move_tx_from_pool_to_current_block(tx2.hash.hex())
        self.node.move_tx_from_pool_to_current_block(txr.hash.hex())

        self.node.save_ledger()
        self.node.save_pool()

        loaded_pool = Pool.load(self.node.pool_hash)
        self.assertEqual(loaded_pool.all_txs(), self.node.pool.all_txs())

        loaded_legder = Ledger.load(self.node.ledger_hash)
        self.assertEqual(loaded_legder.get_current_block().all_txs(
        ), self.node.ledger.get_current_block().all_txs())

        self.node = Node()

        self.assertEqual(loaded_legder.get_current_block().all_txs(
        ), self.node.ledger.get_current_block().all_txs())
        self.assertEqual(loaded_pool.all_txs(), self.node.pool.all_txs())

        self.node.save_all()


if __name__ == '__main__':
    unittest.main()
