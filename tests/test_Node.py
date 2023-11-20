import unittest
from Node import *
# from Transaction import Tx, TxType, REWARD_VALUE
# from User import User
# from BlockChain import *


class TestNode(unittest.TestCase):
    def test_node_functions(self):
        self.node = Node()
        self.username = "autotester"
        self.password = "testertester"
        self.receiver_username = "tester"
        self.receiver_password = "testertester"

        # Test registering a new user
        if not self.node.accounts.user_exists(self.username):
            result = self.node.register(self.username, self.password)
            self.assertEqual(result, NodeActionResult.SUCCESS)
            self.assertTrue(self.node.accounts.user_exists(self.username))
            self.assertEqual(len(self.node.pool.all_txs()), 1)

            # self.assertEqual(self.node.user_wallet.incoming, REWARD_VALUE)
            # self.assertEqual(self.node.user_wallet.outgoing, 0.0)
            # self.assertEqual(self.node.user_wallet.reserved, 0.0)
            # self.assertEqual(self.node.user_wallet.fees, 0.0)
            # self.assertEqual(self.node.user_wallet.available, REWARD_VALUE)

        if not self.node.accounts.user_exists(self.receiver_username):
            result = self.node.register(
                self.receiver_username, self.receiver_password)
            self.assertEqual(result, NodeActionResult.SUCCESS)
            self.assertTrue(self.node.accounts.user_exists(
                self.receiver_username))
            self.assertEqual(len(self.node.pool.all_txs()), 2)

        # Test registering an existing user
        result = self.node.register(self.username, self.password)
        self.assertEqual(result, NodeActionResult.INVALID)
        self.assertTrue(self.node.accounts.user_exists(self.username))

        # Test logging in with correct credentials
        result = self.node.login(self.username, self.password)
        self.assertEqual(result, NodeActionResult.SUCCESS)
        self.assertIsNotNone(self.node.user)
        self.assertIsInstance(self.node.user_wallet, Wallet)

        # Test logging out
        self.node.logout()
        self.assertIsNone(self.node.user)
        self.assertIsNone(self.node.user_wallet)

        # Test logging in with incorrect credentials
        result = self.node.login(self.username, "wrongpassword")
        self.assertEqual(result, NodeActionResult.FAIL)
        self.assertIsNone(self.node.user)
        self.assertIsNone(self.node.user_wallet)

        # Test logging in with non-existing user
        result = self.node.login("nonexistinguser", "password")
        self.assertEqual(result, NodeActionResult.INVALID)
        self.assertIsNone(self.node.user)
        self.assertIsNone(self.node.user_wallet)

        # Test create_tx
        self.node.login(self.username, self.password)

        receiver_public_key = self.node.accounts.get_user(
            self.receiver_username).get_public_key()

        # Test creating a valid transaction through the node
        self.assertEqual(len(self.node.pool.all_txs()), 2)

        self.node.create_tx(1.2, 1.0, 0.2,
                            self.password,
                            receiver_public_key)

        self.assertEqual(len(self.node.pool.all_txs()), 3)

    # def test_validate_previous_block(self):
    #     # Test validating previous block with correct password
    #     self.node.login(self.username, self.password)

    #     prev_block.mine()
    #     result = self.node.validate_previous_block(self.password)
    #     self.assertEqual(result, NodeActionResult.SUCCESS)
    #     self.assertEqual(prev_block.state(), BlockState.VALIDATED)
    #     self.assertEqual(len(self.node.pool.all_txs()), 1)
    #     self.assertEqual(self.node.pool.all_txs()[tx.hash], tx)

    #     # Test validating previous block with incorrect password
    #     result = self.node.validate_previous_block("wrongpassword")
    #     self.assertEqual(result, NodeActionResult.FAIL)
    #     self.assertEqual(prev_block.state(), BlockState.VALIDATED)
    #     self.assertEqual(len(self.node.pool.all_txs()), 1)
    #     self.assertEqual(self.node.pool.all_txs()[tx.hash], tx)

    #     # Test validating previous block when no previous block exists
    #     self.node.curr_block = CBlock()
    #     result = self.node.validate_previous_block(self.password)
    #     self.assertEqual(result, NodeActionResult.INVALID)

    # def test_mine_block(self):
    #     # Test mining a block with valid transactions
    #     username = "testuser"
    #     password = "testpassword"
    #     self.node.register(username, password)
    #     self.node.login(username, password)
    #     tx = Tx(1.0, 1.0, 0.0, self.node.user_wallet.public_key,
    #             self.node.user_wallet.public_key, TxType.NORMAL)
    #     tx.sign(self.node.user_wallet.private_key)
    #     self.node.pool.add_tx(tx)
    #     result = self.node.mine_block()
    #     self.assertEqual(result, NodeActionResult.SUCCESS)
    #     self.assertEqual(self.node.curr_block.state(), BlockState.MINED)
    #     self.assertEqual(len(self.node.ledger.blocks), 2)
    #     self.assertEqual(len(self.node.pool.all_txs()), 1)
    #     self.assertEqual(self.node.pool.all_txs()[tx.hash], tx)

    #     # Test mining a block with invalid transactions
    #     tx = Tx(100.0, 1.0, 0.0, self.node.user_wallet.public_key,
    #             self.node.user_wallet.public_key, TxType.NORMAL)
    #     tx.sign(self.node.user_wallet.private_key)
    #     self.node.pool.add_tx(tx)
    #     result = self.node.mine_block()
    #     self.assertEqual(result, NodeActionResult.FAIL)
    #     self.assertEqual(self.node.curr_block.state(), BlockState.READY)
    #     self.assertEqual(len(self.node.ledger.blocks), 2)
    #     self.assertEqual(len(self.node.pool.all_txs()), 2)

    # def test_auto_fill_block(self):
    #     # Test auto-filling a block with transactions
    #     for i in range(12):
    #         tx = Tx(1.0, 1.0, 0.0, self.node.accounts.get_user("admin").get_public_key(
    #         ), self.node.accounts.get_user("admin").get_public_key(), TxType.REWARD)
    #         tx.sign(self.node.accounts.get_user(
    #             "admin").get_rsa_keys("admin")[0])
    #         self.node.pool.add_tx(tx)
    #     result = self.node.auto_fill_block()
    #     self.assertEqual(result, NodeActionResult.SUCCESS)
    #     self.assertEqual(len(self.node.curr_block.txs), 10)
    #     self.assertEqual(len(self.node.pool.all_txs()), 2)
    #     self.assertEqual(
    #         len([tx for tx in self.node.curr_block.txs if tx.type == TxType.REWARD]), 5)
    #     self.assertEqual(
    #         len([tx for tx in self.node.curr_block.txs if tx.type == TxType.NORMAL]), 5)

    #     # Test auto-filling a block with no transactions
    #     self.node.curr_block = CBlock()
    #     result = self.node.auto_fill_block()
    #     self.assertEqual(result, NodeActionResult.INVALID)


if __name__ == '__main__':
    unittest.main()
