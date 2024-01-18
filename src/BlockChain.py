"""
Mining:
■ A block must be mined between 10 to 20 seconds. A proof of work is implemented for this purpose, which creates a specific hash with a specific number of leading zero. 
(This timing is for testing while assessing and grading your code. Do not use any sleep or delay function to adjust the time if it is too fast).
■ A miner will receive 50 coins, as a mining reward for a successful block added to the chain.
■ A new block could be mined, if there are a minimum of 5 and a maximum of 10 valid transactions on the pool.
■ A minimum of 3 minutes interval must be between every two consequent blocks.
■ A new block could be mined after the last block, only if every previous block in the chain has at least 3 valid flags.

Mining
Once a user logs in to the system, they can decide to mine a new block and receive reward for the proof of work. 
For this, the node should check the pool for valid transactions, and find a minimum of 5 and a maximum of 10 valid transactions to be added to the new block. 
A motivation for a node to include a transaction in their new block for mining is the transaction fee. 
A node is free to have a strategy to choose specific transactions and how many transactions to be added to the new block. 
However, the strategy must ensure that the selection process is not biased to a specific node. 
It means that for example a node cannot wait only for its own transactions or always ignore the transactions with zero transaction fee or lower fee. 
It can choose the highest fee first, but if there are some other transactions in the pool, they need to be finally included in a block.
During this process, a miner will check the transactions and validate them. Any invalid transaction must be flagged as invalid, in the pool. 
These invalid transactions must be automatically canceled and removed from the pool by the creator of the transactions upon their next login.
Once a block is created by a node, the next three logged in users (nodes) must check the validity of the created block. 
These nodes will fully check the block to ensure a valid block is created by the miner. If the block is valid, they flag it as valid, otherwise they flag it as invalid.
	■ If the new block is flagged as valid by these three nodes (three different logged in users), 
    then the third validator node is responsible to create a new transaction to reward the miner of the block. 
    This reward transaction could be included in the next mining process. 
    If a block successfully got validated by three other nodes, it does not need to be validated by any other nodes later. 
    (Note that the block cannot be validated by the creator of the block.)
	■ If the new block is flagged as invalid (rejected) by at least three other nodes, before getting three valid flags, 
    then the third rejector node is also responsible to return all the transactions of the rejected block back to the pool. 
    In this case, if the block is rejected because of some invalid transactions, 
    those invalid transactions must be also flagged as invalid on the pool to be nullified by the creator of the transaction upon login. 
    Other valid transactions in the rejected block must be returned to the pool, waiting for the next mining process to be included in a new block again.
"""

from __future__ import annotations
from enum import Enum
from time import time
from math import fsum, isclose
import secrets
from typing import NamedTuple
from src.Signature import *
from src.Transaction import *
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

LEADING_ZEROES = 2
NEXT_CHAR_LIMIT = 16
MATURITY_TIME = 180
TX_MINIMUM = 5
TX_MAXIMUM = 10
REQUIRED_FLAGS = 3


class BlockState(Enum):
    NEW = 0
    READY = 1
    MINED = 2
    VALIDATED = 3

    def __le__(self, other: BlockState) -> bool:
        return self.value <= other.value

    def __ge__(self, other: BlockState) -> bool:
        return self.value >= other.value

    def __eq__(self, other: BlockState) -> bool:
        return self.value == other.value


class ValidationFlag(NamedTuple):
    block_id: int
    public_key: bytes
    signature: bytes


class CBlock:
    def __init__(self, previousBlock: CBlock = None):
        self.txs: dict[str, Tx] = dict()
        self.previousBlock = previousBlock
        self.previousHash = None if previousBlock is None else previousBlock.compute_hash()
        self.next_char_limit = NEXT_CHAR_LIMIT
        self.nonce = secrets.randbelow(2**256)
        self.hash = None
        self.minted_at = time()
        self.mined_at = None
        self.mined_by = None
        self.signature = None
        self.validation_flags: list[(bytes, bytes)] = []
        self.id = 0 if previousBlock is None else previousBlock.id + 1

    def __repr__(self) -> str:
        return f"Block {self.id} [{self.state()}] : {self.hash.hex() if self.hash is not None else 'no hash yet'}"

    def compute_hash(self) -> bytes:
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.id), 'utf8'))
        digest.update(bytes(str(self.txs), 'utf8'))
        digest.update(bytes(str(self.previousHash), 'utf8'))
        digest.update(bytes(str(self.nonce), 'utf8'))
        digest.update(bytes(str(self.next_char_limit), 'utf8'))
        digest.update(bytes(str(self.minted_at), 'utf8'))
        digest.update(bytes(str(self.mined_at), 'utf8'))
        digest.update(self.mined_by if self.mined_by is not None else bytes(
            str("not mined yet"), 'utf8'))
        return digest.finalize()

    def add_tx(self, tx: Tx) -> bool:
        if tx is not None and tx.is_valid() and self.state() <= BlockState.READY:
            self.txs.update({tx.hash.hex(): tx})
            return True
        return False

    def cancel_tx(self, tx_hash: str, sender_addr: bytes) -> bool:
        tx: Tx = self.txs.get(tx_hash)
        if tx is not None and tx.type != REWARD and tx.signed_by(sender_addr) and tx.sent_by(sender_addr):
            del self.txs[tx_hash]
            return True
        return False

    def get_tx(self, tx_hash: str) -> Tx | None:
        return self.txs.get(tx_hash)

    def all_txs(self) -> dict[str, Tx]:
        return self.txs.copy()

    def get_tx_fees(self) -> float:
        return fsum(tx.fee for tx in self.txs.values())

    def pop_tx_by_hash(self, tx_hash: str) -> Tx | None:
        if tx_hash in self.txs.keys():
            return self.txs.pop(tx_hash)
        return None

    def get_txs_by_public_key(self, public_key: bytes) -> dict[str, Tx]:
        return {tx_hash: tx for tx_hash, tx in self.txs.items() if tx.sender == public_key or tx.receiver == public_key}

    def __count_totals(self) -> tuple[float, float, float]:
        return (fsum([tx.get_input() for tx in self.txs.values()]),
                fsum([tx.get_output() for tx in self.txs.values()]),
                fsum([tx.get_fee() for tx in self.txs.values()]))

    def __is_balanced(self) -> bool:
        total_in, total_out, fee = self.__count_totals()
        return isclose(total_in, fsum((total_out, fee)))

    def __has_valid_txs(self) -> bool:
        return all(tx.is_valid() for tx in self.txs.values())

    def chain_is_valid(self) -> bool:
        return self.__hash_is_valid() and (self.previousBlock is None or (self.previousHash == self.previousBlock.compute_hash() and self.previousBlock.chain_is_valid()))

    def __hash_is_valid(self) -> bool:
        return self.hash is None or self.hash == self.compute_hash() and self.good_nonce(self.hash) and verify(self.hash, self.signature, decode_public_key(self.mined_by))

    def block_is_valid(self) -> bool:
        return self.__hash_is_valid() and self.chain_is_valid() and self.__has_valid_txs() and self.__is_balanced()

    def was_validated(self) -> bool:
        # prune any invalid flags
        self.validation_flags = [(sig, pub) for sig, pub in self.validation_flags
                                 if verify(self.hash, sig, decode_public_key(pub))]
        # A block is considered validated if it has at least 3 valid flags.
        return len(self.validation_flags) >= REQUIRED_FLAGS and self.__hash_is_valid() and all(verify(self.hash, sig, decode_public_key(pub)) for sig, pub in self.validation_flags)

    def was_validated_by(self, pub_key: rsa.RSAPublicKey) -> bool:
        return any((verify(self.hash, sig, pub_key) and encode_public_key(pub_key) == pub) for sig, pub in self.validation_flags)

    def get_validation_flag(self, pub_key: rsa.RSAPublicKey) -> ValidationFlag | None:
        for sig, pub in self.validation_flags:
            if verify(self.hash, sig, pub_key) and encode_public_key(pub_key) == pub:
                return ValidationFlag(self.id, pub, sig)
        return None

    def add_validation_flag(self, sig: bytes, pub: bytes) -> bool:
        if self.hash is not None and verify(self.hash, sig, decode_public_key(pub)) and not self.was_validated_by(decode_public_key(pub)) and self.block_is_valid():
            self.validation_flags.append((sig, pub))
            return True
        return False

    def validate_block(self, priv_key: rsa.RSAPrivateKey, pub_key: rsa.RSAPublicKey) -> bool:
        if self.hash is not None and not self.was_validated_by(pub_key) and self.block_is_valid():
            signature = sign(self.hash, priv_key)
            self.validation_flags.append((signature,
                                          encode_public_key(pub_key)))
            return True
        return False

    def __ready_to_mine(self) -> bool:
        return self.hash is None and 5 <= len(self.txs) <= 10 and (self.previousBlock is None
                                                                   or time() - self.previousBlock.mined_at >= MATURITY_TIME
                                                                   and self.previousBlock.was_validated()) and self.block_is_valid()

    def mine(self, priv_key: rsa.RSAPrivateKey, pub_key: rsa.RSAPublicKey) -> CBlock:
        # check mining conditions
        if not self.__ready_to_mine():
            return self  # return current block if conditions are not met

        self.mined_by = encode_public_key(pub_key)  # save miner
        self.mined_at = time()  # timestamp
        hash_candidate = self.compute_hash()  # get initial hash candidate
        start = time()  # set timer

        # do until hash is sufficiently complex
        while not self.good_nonce(hash_candidate):
            self.nonce = secrets.randbelow(2**256)  # generate new nonce
            self.mined_at = time()  # timestamp
            hash_candidate = self.compute_hash()  # get new hash candidate
            if time() - start > 2:
                # expand valid hashpool every 2 seconds
                self.next_char_limit += NEXT_CHAR_LIMIT
                start = time()  # reset timer

        self.hash = hash_candidate  # save final hash
        self.signature = sign(self.hash, priv_key)  # sign block
        return CBlock(self)  # return new block

    def good_nonce(self, hash_candidate: bytes) -> bool:
        return hash_candidate.startswith(b'0' * LEADING_ZEROES) and hash_candidate[LEADING_ZEROES] <= self.next_char_limit

    def state(self) -> BlockState:
        if self.hash is None and not self.__ready_to_mine():
            return BlockState.NEW
        elif self.__ready_to_mine():
            return BlockState.READY
        elif self.hash is not None and self.mined_at is not None and not self.was_validated():
            return BlockState.MINED
        elif self.was_validated():
            return BlockState.VALIDATED
