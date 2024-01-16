"""
Data files
As shown in the Figure 1, there are three data files required for the system to meet the required functionalities.
The purpose of each file is briefly described below:
    ■ The Database
        A relational database is required to store data of the registered users, including username, hash of password, private key, and public key,
        and more information if needed (e.g., recovery phrase key). It is obvious that this database must be securely implemented. 
        This database must be used only for the users’ information and no data from the blockchain or the pool should be stored in the relational database.
    ■ The Ledger
        This is the main file to store all data of transactions. It must be developed according to requirements of blockchain data structure, 
        including all the required components (for example, hash of block, metadata, transaction data, nonce, etc.)
    ■ The Pool
        As this application can serve only one user at a time, 
        some changes of the blockchain (e.g., requests for transactions) needs to be temporarily placed in a file, 
        until the validation process or consensus process is completed. 
        The pool file is mainly used for this synchronization purpose.
        This file contains a list of transactions, and its format must be according to the structure of the transactions (the same format with the ledger). 
        Do not use a relational database, JSON, csv, XML, or any other similar standard data transmission protocols or format. 
        (In the practicum 6, we have already discussed and learned how to save and load transactions on a file).
        In the final assignment part 1, we have only one instance of each file, shared among all users (only one ledger, one user database, and only one pool). 
        As at any specific time, only one user can access the file, it is not needed (and not allowed) to have a separate copy of files for each node.
"""
from __future__ import annotations
import pickle
from pathlib import Path
from typing import Mapping
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from src.Transaction import *
from src.BlockChain import *
from src.User import User


def compose_relative_filepath(filename: str) -> Path:
    base_path = Path(__file__).parent
    file_path = (base_path / f"../data/{filename}").resolve()
    return file_path


def file_hash(path: Path) -> bytes | None:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    try:
        with open(path, "rb") as f:
            content = f.read()
            digest.update(content)
            return digest.finalize()
    except:
        return None


def compare_hash(path: Path, hash: bytes) -> bool:
    return file_hash(path) == hash


def save_and_return_hash(file: str, data: object) -> bytes | None:
    path = compose_relative_filepath(file)
    with open(path, "wb+") as f:
        pickle.dump(data, f,  protocol=pickle.HIGHEST_PROTOCOL)
    return file_hash(path)


def load_if_valid(file: str, hash: bytes) -> object | None:
    try:
        path = compose_relative_filepath(file)
        if compare_hash(path, hash):
            with open(path, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        return None


class Accounts:
    def __init__(self):
        self.users: dict[str, User] = dict()

    def add_user(self, user: User) -> bool:
        if not user.username in self.users.keys():
            self.users.update({user.username: user})
            return True
        return False

    def get_user(self, username: str) -> User:
        return self.users.get(username)

    def get_user_directory(self) -> dict[str, bytes]:
        return self.users.copy()

    def get_user_by_public_key(self, public_key: bytes) -> User | None:
        for user in self.users.values():
            if user.public_key == public_key:
                return user
        return None

    def user_exists(self, username: str) -> bool:
        return username in self.users.keys()

    def save(self) -> bytes | None:
        return save_and_return_hash("database.dat", self)

    @staticmethod
    def load(acc_hash: bytes) -> Accounts:
        accounts: Accounts = load_if_valid("database.dat", acc_hash)
        return accounts if accounts is not None else Accounts()


class Ledger:
    def __init__(self):
        self.head: CBlock = None

    def add_block(self, block: CBlock) -> bool:
        if block.block_is_valid() and (self.head is None or self.head == block.previousBlock):
            self.head = block
            return True
        return False

    def add_mined_block(self, block: CBlock) -> bool:
        # if block is valid, mined and previous block is validated
        if (block.block_is_valid()
                and block.state() >= BlockState.MINED
                and (block.previousBlock is None or block.previousBlock.state() == BlockState.VALIDATED)
            ):
            # if head is the block's previous block, or
            # block is the current head, block's previous block is the head's previous block, block was mined before the head, or
            # block is the previous block, it's previous block is the head's previous block's and was mined before the head's previous block
            if (self.head == block.previousBlock
                ) or (self.head.id == block.id
                      and self.head.previousBlock == block.previousBlock
                      and (self.head.mined_at is None or self.head.mined_at > block.mined_at)
                      ) or (self.head.previousBlock is not None and self.head.previousBlock.id == block.id
                            and self.head.previousBlock.previousBlock == block.previousBlock
                            and self.head.previousBlock.mined_at > block.mined_at
                            ):
                # add a new block built on the mined block and make it the head
                self.head = CBlock(block)
                return True
        return False

    def get_block_by_id(self, block_id: int) -> CBlock:
        if self.head.id == block_id:
            return self.head
        elif self.head.id < block_id < 0:
            return None
        else:
            # traverse the chain
            curr = self.head
            while curr.previousBlock is not None:
                if curr.previousBlock.id == block_id:
                    return curr.previousBlock
                curr = curr.previousBlock
            return None

    def get_current_block(self) -> CBlock:
        return self.head

    def all_txs_from_chain(self) -> dict[str, Tx]:
        # traverse chain and collect all txs
        curr = self.head
        txs = dict()
        txs.update(curr.all_txs())

        while curr.previousBlock is not None:
            curr = curr.previousBlock
            txs.update(curr.all_txs())

    def get_txs_by_public_key(self, public_key: bytes) -> dict[str, Tx]:
        # traverse chain and return all processed txs by public key
        curr = self.head
        txs = dict()

        while curr is not None:
            if curr.state() >= BlockState.MINED:
                txs.update(curr.get_txs_by_public_key(public_key))
            curr = curr.previousBlock

        return txs

    def get_tx_fees_by_public_key(self, public_key: bytes) -> float:
        # traverse chain and return all tx fees by public key
        curr = self.head
        fees = 0.0

        while curr is not None:
            if curr.was_validated() and curr.mined_by == public_key:
                fees = fsum((fees, curr.get_tx_fees()))

            curr = curr.previousBlock

        return fees

    def get_pending_txs_by_public_key(self, public_key: bytes) -> dict[str, Tx]:
        # return all pending txs from the current block by public key
        return self.head.get_txs_by_public_key(public_key)

    def save(self) -> bytes | None:
        return save_and_return_hash("ledger.dat", self)

    @staticmethod
    def load(ledger_hash: bytes) -> Ledger:
        ledger: Ledger = load_if_valid("ledger.dat", ledger_hash)
        return ledger if ledger is not None else Ledger()


class Pool:
    def __init__(self):
        self.txs: dict[str, Tx] = dict()

    def add_tx(self, tx: Tx) -> bool:
        if tx.is_valid():
            self.txs.update({tx.hash.hex(): tx})
            return True
        return False

    def get_tx(self, tx_hash: str) -> Tx | None:
        return self.txs.get(tx_hash)

    def cancel_tx(self, tx_hash: str, sender_addr: bytes) -> bool:
        tx: Tx = self.txs.get(tx_hash)
        if tx is not None and tx.type != REWARD and tx.signed_by(sender_addr) and tx.sent_by(sender_addr):
            del self.txs[tx_hash]
            return True
        return False

    def pop_tx(self, tx_hash: str) -> Tx | None:
        if tx_hash in self.txs.keys():
            return self.txs.pop(tx_hash)
        return None

    def all_txs(self) -> dict[str, Tx]:
        return self.txs.copy()

    def get_txs_by_public_key(self, public_key: bytes) -> dict[str, Tx]:
        return {tx_hash: tx for tx_hash, tx in self.txs.items() if tx.sender == public_key or tx.receiver == public_key}

    def save(self) -> bytes | None:
        return save_and_return_hash("pool.dat", self)

    @staticmethod
    def load(pool_hash: bytes) -> Pool:
        pool: Pool = load_if_valid("pool.dat", pool_hash)
        return pool if pool is not None else Pool()
