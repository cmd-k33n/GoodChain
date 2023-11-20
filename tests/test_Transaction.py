import unittest
from Transaction import Tx, NORMAL, REWARD, REWARD_VALUE
from Signature import generate_keys


class TestTx(unittest.TestCase):
    def setUp(self):
        self.private_key, self.public_key = generate_keys()

    def test_normal_tx_is_valid(self):
        tx = Tx(10.1, 10.0, 0.1, self.public_key, self.public_key)
        tx.sign(self.private_key)
        self.assertTrue(tx.is_valid())

    def test_normal_tx_with_invalid_input_output(self):
        tx = Tx(10.0, 5.0, 0.1, self.public_key, self.public_key)
        tx.sign(self.private_key)
        self.assertFalse(tx.is_valid())

    def test_reward_tx_is_valid(self):
        tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                self.public_key,
                self.public_key,
                REWARD
                )
        tx.sign(self.private_key)
        self.assertTrue(tx.is_valid())

    def test_reward_tx_with_invalid_output(self):
        tx = Tx(0.0, 5.0, 0.0, self.public_key, self.public_key, REWARD)
        tx.sign(self.private_key)
        self.assertFalse(tx.is_valid())

    def test_reward_tx_with_invalid_type(self):
        tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                self.public_key,
                self.public_key,
                NORMAL
                )
        tx.sign(self.private_key)
        self.assertFalse(tx.is_valid())

    def test_tx_with_invalid_signature(self):
        tx1 = Tx(10.1, 10.0, 0.1, self.public_key, self.public_key)
        tx1.sign(self.private_key)
        tx2 = Tx(10.1, 10.0, 0.1, self.public_key, self.public_key)
        self.assertFalse(tx2.is_valid())

    def test_tx_with_invalid_sender(self):
        private_key2, public_key2 = generate_keys()
        tx = Tx(10.1, 10.0, 0.1, self.public_key, public_key2)
        tx.sign(private_key2)
        self.assertFalse(tx.is_valid())

    def test_tx_with_invalid_hash(self):
        tx = Tx(10.1, 10.0, 0.1, self.public_key, self.public_key)
        tx.hash = b'invalid hash'
        tx.sig = b'invalid signature'
        self.assertFalse(tx.is_valid())


if __name__ == '__main__':
    unittest.main()
