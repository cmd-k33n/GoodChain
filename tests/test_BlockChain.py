import unittest
from time import sleep
from BlockChain import *
from Transaction import *
from Signature import *


class TestBlockChain(unittest.TestCase):
    def setUp(self):
        self.sender_private_key, self.sender_public_key = generate_keys()
        self.receiver_private_key, self.receiver_public_key = generate_keys()
        self.other_private_key, self.other_public_key = generate_keys()

        self.block: CBlock = CBlock()

    def test_everything_bagel(self):
        tx = Tx(10.1, 10.0, 0.1,
                self.sender_public_key,
                self.receiver_public_key
                )
        tx.sign(self.sender_private_key)
        self.assertTrue(self.block.add_tx(tx))
        self.assertEqual(len(self.block.txs), 1)

        tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                self.sender_public_key,
                self.receiver_public_key,
                REWARD
                )
        tx.sign(self.sender_private_key)
        self.assertTrue(self.block.add_tx(tx))
        self.assertEqual(len(self.block.txs), 2)

        tx = Tx(10.1, 10.0, 0.1,
                self.sender_public_key,
                self.receiver_public_key
                )
        tx.sign(self.sender_private_key)
        self.block.add_tx(tx)
        self.assertTrue(self.block.cancel_tx(tx.hash.hex(),
                                             encode_public_key(self.sender_public_key)))
        self.assertEqual(len(self.block.txs), 2)

        # test reward cancel
        tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                self.sender_public_key,
                self.receiver_public_key,
                REWARD
                )
        tx.sign(self.sender_private_key)
        self.block.add_tx(tx)
        self.assertFalse(self.block.cancel_tx(tx.hash,
                                              encode_public_key(self.sender_public_key)))
        self.assertEqual(len(self.block.txs), 3)
        self.block.txs.clear()

        # test get tx
        tx = Tx(10.1, 10.0, 0.1,
                self.sender_public_key,
                self.receiver_public_key)
        tx.sign(self.sender_private_key)
        self.block.add_tx(tx)
        self.assertEqual(self.block.get_tx(tx.hash.hex()), tx)

        # test get tx fees
        tx1 = Tx(10.1, 10.0, 0.1,
                 self.sender_public_key,
                 self.receiver_public_key)
        tx1.sign(self.sender_private_key)
        self.block.add_tx(tx1)
        tx2 = Tx(5.5, 5.0, 0.5,
                 self.sender_public_key,
                 self.receiver_public_key)
        tx2.sign(self.sender_private_key)
        self.block.add_tx(tx2)
        self.assertAlmostEqual(self.block.get_tx_fees(), 0.7)
        self.block.txs.clear()

        tx1 = Tx(10.1, 10.0, 0.1,
                 self.sender_public_key,
                 self.receiver_public_key)
        tx1.sign(self.sender_private_key)
        self.block.add_tx(tx1)
        tx2 = Tx(5.05, 5.0, 0.05,
                 self.sender_public_key,
                 self.receiver_public_key)
        tx2.sign(self.sender_private_key)
        self.block.add_tx(tx2)
        self.assertEqual(self.block.pop_tx_by_hash(tx1.hash.hex()), tx1)
        self.assertEqual(len(self.block.txs), 1)
        self.assertEqual(self.block.pop_tx_by_hash(tx2.hash.hex()), tx2)
        self.assertEqual(len(self.block.txs), 0)

        self.block.txs.clear()

        tx1 = Tx(10.1, 10.0, 0.1,
                 self.sender_public_key,
                 self.receiver_public_key)
        tx1.sign(self.sender_private_key)
        self.block.add_tx(tx1)
        tx2 = Tx(5.05, 5.0, 0.05,
                 self.sender_public_key,
                 self.other_public_key)
        tx2.sign(self.sender_private_key)
        self.block.add_tx(tx2)
        self.assertEqual(self.block.get_txs_by_public_key(encode_public_key(self.receiver_public_key)),
                         {tx1.hash.hex(): tx1})
        self.assertEqual(self.block.get_txs_by_public_key(encode_public_key(self.other_public_key)),
                         {tx2.hash.hex(): tx2})
        self.assertEqual(self.block.get_txs_by_public_key(encode_public_key(self.sender_public_key)),
                         {tx1.hash.hex(): tx1, tx2.hash.hex(): tx2})
        self.block.txs.clear()

        tx1 = Tx(10.1, 10.0, 0.1,
                 self.sender_public_key,
                 self.sender_public_key
                 )
        tx1.sign(self.sender_private_key)
        self.block.add_tx(tx1)
        self.assertTrue(self.block.block_is_valid())
        tx2 = Tx(10.0, 5.0, 0.1,
                 self.sender_public_key,
                 self.sender_public_key
                 )
        tx2.sign(self.sender_private_key)
        self.block.add_tx(tx2)
        self.assertEqual(len(self.block.txs), 1)
        self.assertTrue(self.block.block_is_valid())
        self.block.txs.clear()

        self.assertEqual(self.block.state(), BlockState.NEW)
        self.assertTrue(self.block.block_is_valid())
        self.assertFalse(self.block._CBlock__ready_to_mine())

        # fill with 5 txs
        for i in range(5):
            tx = Tx(1.1, 1.0, 0.1,
                    self.sender_public_key,
                    self.receiver_public_key
                    )
            tx.sign(self.sender_private_key)
            self.assertTrue(self.block.add_tx(tx))
            sleep(1)
            self.assertEqual(len(self.block.txs), i+1)

        # count totals and check if block is balanced
        total_in, total_out, fee = self.block._CBlock__count_totals()
        self.assertAlmostEqual(total_in, 5.5)
        self.assertAlmostEqual(total_out, 5.0)
        self.assertAlmostEqual(fee, 0.5)
        self.assertTrue(self.block._CBlock__is_balanced())

        # add reward tx
        tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                self.sender_public_key,
                self.other_public_key,
                REWARD
                )
        tx.sign(self.sender_private_key)
        self.block.add_tx(tx)
        self.assertEqual(len(self.block.txs), 6)
        self.assertTrue(self.block._CBlock__is_balanced())

        # check if block is ready to mine
        self.assertTrue(self.block.block_is_valid())
        self.assertTrue(self.block._CBlock__ready_to_mine())
        self.assertEqual(self.block.state(), BlockState.READY)

        # attempt to mine
        block2 = self.block.mine(self.sender_private_key,
                                 self.sender_public_key)
        self.assertFalse(block2 is self.block)

        # check if block was mined
        self.assertEqual(self.block.state(), BlockState.MINED)
        self.assertEqual(block2.state(), BlockState.NEW)
        self.assertIsNotNone(self.block.hash)
        self.assertIsNotNone(self.block.mined_at)
        self.assertTrue(verify(self.block.hash,
                               self.block.signature,
                               decode_public_key(self.block.mined_by)))
        self.assertTrue(verify(self.block.hash,
                               self.block.signature,
                               self.sender_public_key))
        self.assertEqual(self.block.mined_by,
                         encode_public_key(self.sender_public_key))
        self.assertEqual(block2.previousHash, self.block.compute_hash())
        self.assertTrue(block2.chain_is_valid())
        self.assertTrue(block2.block_is_valid())
        self.assertFalse(self.block.was_validated())
        self.assertFalse(block2._CBlock__ready_to_mine())

        # add 2 validation flags to first block
        self.block.validate_block(
            self.sender_private_key, self.sender_public_key)
        self.block.validate_block(self.receiver_private_key,
                                  self.receiver_public_key)

        # attempt to add first validation 2nd time
        self.block.validate_block(
            self.sender_private_key, self.sender_public_key)
        self.assertEqual(len(self.block.validation_flags), 2)
        self.assertFalse(self.block.was_validated())

        # add final validation flag to first block
        self.block.validate_block(
            self.other_private_key, self.other_public_key)

        # check if block1 was validated
        self.assertEqual(self.block.state(), BlockState.VALIDATED)
        self.assertTrue(self.block.was_validated())

        # try to add transaction to block1 after mining (should fail)
        tx = Tx(1.1, 1.0, 0.1,
                self.sender_public_key,
                self.receiver_public_key
                )
        tx.sign(self.sender_private_key)
        self.assertFalse(self.block.add_tx(tx))

        # check block2 validity
        self.assertTrue(block2.block_is_valid())
        self.assertFalse(block2.was_validated())

        # fill second block with 9 txs and one reward tx
        for i in range(9):
            tx = Tx(1.1, 1.0, 0.1,
                    self.sender_public_key,
                    self.receiver_public_key
                    )
            tx.sign(self.sender_private_key)
            block2.add_tx(tx)
            sleep(1)
            self.assertEqual(len(block2.txs), i + 1)

        # add reward tx
        tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                self.sender_public_key,
                self.sender_public_key,
                REWARD
                )
        tx.sign(self.sender_private_key)
        block2.add_tx(tx)
        self.assertEqual(len(block2.txs), 10)

        # attempt to mine early
        early_block = block2.mine(self.sender_private_key,
                                  self.sender_public_key)
        self.assertTrue(early_block is block2)
        self.assertEqual(block2.state(), BlockState.NEW)

        # wait 180 seconds for block2 to be ready
        while time() - block2.previousBlock.mined_at < 180:
            sleep(1)

        # check if block2 is ready to mine
        self.assertEqual(block2.state(), BlockState.READY)

        # attempt to mine
        block3 = block2.mine(self.sender_private_key,
                             self.sender_public_key)
        self.assertFalse(block3 is block2)

        # check if block2 was mined correctly
        self.assertEqual(block2.state(), BlockState.MINED)
        self.assertEqual(block3.state(), BlockState.NEW)
        self.assertIsNotNone(block2.hash)
        self.assertIsNotNone(block2.mined_at)
        self.assertEqual(block2.mined_by,
                         encode_public_key(self.sender_public_key))


if __name__ == '__main__':
    unittest.main()
