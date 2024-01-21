"""
General requirements:
■ The system must be built based on blockchain data structure.
■ There is no administrator or central authority to manage or control the system.
■ There are two types of users: public users and registered users (nodes)
■ A user can add a new block to the chain if the block is successfully mined.
■ When a transaction is created by a user, the transaction will be placed in a transactions pool.
■ A user can always check the validation of the whole chain.
■ A user can always check the validation of a specific block and add a validation flag to a valid block.
■ The system must always validate the blockchain for any tamper on every reading or writing or any other operation on the blockchain.
■ A user can see the data of every block.
■ A user can see the information of the whole blockchain, including the number of blocks and the total number of transactions.
■ A user can cancel of modify their own pending transactions on the pool.


Public user
A public user is a user who is not registered or signed up in the application. This user has some limited access to the system.
■ Any user can freely register (sign up) in the application.
■ Any user can explore the public ledger and view the data of each block.

Registration (Sign up):
Once a public user signed up in the application, a node is created for the user. We will call this user a “node user”, or “logged-in user”, or only a “node” for short.
■ A user must provide a unique username and a password when registering in the system.
■ A node user will receive 50 coins as a sign-up reward, after registration.
■ A unique pair of private key and public key must be created for a node user, after registration.

Node user (Logged in user)
This user can login to the system and perform some specific activities, such as transferring coin, mining a block, etc.
■ A node user has a wallet.
■ A node user can send some coins from their wallet to the other registered users in the system.
■ A node user can receive some coins in their wallet from the other registered users in the system.
■ A node user can try mining a new block.
■ A node user can see their balance on the user page.
■ A node user can see the history of their own transactions thorough a menu.
■ A node user can view the current ongoing transactions on the pool

Notifications when a user logs in
When a user logs in to the system, appropriate notifications should be displayed to the user. These notifications could include any relevant information and changes on the status of the blockchain and pool, plus any other relevant pending activities. Some of the important required notifications are listed below:
● General information of the blockchain (the size of blockchain, number of transactions, etc.)
● Users mined block status (if a user already mined a block and the block was on pending for verification by other nodes
● Any block which was on pending and is confirmed or rejected by this user after login
● Reward notification if there was any reward pending for confirmation from other nodes
● New added block(s) since the last login (already confirmed by other nodes or waiting for a confirmation)
● Rejected transactions of the user
● Successful transactions of the user
You may need to add more notifications.

Automatic functions of nodes upon login
Once a user logs in to the system (which means a node is active), the node must perform some specific actions, if required. These activities are explained in detail in different sections of this system.

For example, if there is a new block created by another node, but it is not yet validated by enough nodes and not finalized, then the logged in node must automatically start a validation process of the new block. Another example is if earlier a transaction was ordered by this node, and the transaction was rejected for some reason and flagged as invalid, the transaction must be canceled by the node. There might be some other functions which need to be automatically managed by a node.

"""
from __future__ import annotations
import pickle
from queue import Queue
from threading import Thread
from typing import NamedTuple
from time import sleep
from src.Data import Accounts, Ledger, Pool, compose_relative_filepath
from src.BlockChain import *
from src.Transaction import Tx, REWARD, REWARD_VALUE, NORMAL
from src.Signature import generate_keys, encode_keys
from src.User import User
from src.SocketUtil import NODES, send_object, start_listening_thread, broadcast, received_objects, NODE_PORT, NODE_IP


class NodeActionResult(Enum):
    SUCCESS = 0
    FAIL = 1
    INVALID = 2


class Wallet(NamedTuple):
    processed: dict[str, Tx]
    pending: dict[str, Tx]
    incoming: float
    outgoing: float
    reserved: float
    fees: float
    available: float


# Queue to pass system messages to GUI
system_messages = Queue()


class Node:
    def __init__(self):
        self.acc_hash, self.ledger_hash, self.pool_hash = self.__get_stored_hashes()
        self.accounts: Accounts = Accounts.load(self.acc_hash)
        self.ledger: Ledger = Ledger.load(self.ledger_hash)
        self.pool: Pool = Pool.load(self.pool_hash)
        self.user: User = None
        self.user_wallet: Wallet = None
        self.curr_block: CBlock = self.ledger.get_current_block()
        if len(self.accounts.users) == 0 and self.ledger.get_current_block() is None:
            # Create system files upon minting the genesis block
            self.ledger.add_block(CBlock())
            self.curr_block = self.ledger.get_current_block()
            self.save_all()

        # launch Network Interface
        start_listening_thread()
        # launch object receiver
        self.__start_receiving_objects()
        # launch sync with peers
        self.node_summaries = dict[str, NodeSummary]()
        self.__start_syncing_with_peers()

    def save_all(self):
        self.acc_hash = self.accounts.save()
        self.ledger_hash = self.ledger.save()
        self.pool_hash = self.pool.save()
        self.__set_stored_hashes()

    def save_accounts(self):
        self.acc_hash = self.accounts.save()
        self.__set_stored_hashes()

    def save_ledger(self):
        # if self.ledger.get_current_block().block_is_valid():
        self.ledger_hash = self.ledger.save()
        self.__set_stored_hashes()

    def save_pool(self):
        self.pool_hash = self.pool.save()
        self.__set_stored_hashes()

    def __get_stored_hashes(self):
        # TODO: Get from envrionment variables ACC_HASH, LEDGER_HASH, POOL_HASH
        try:
            hashfile = compose_relative_filepath('file_hashes.dat')
            with open(hashfile, 'rb') as f:
                return pickle.load(f)
        except:
            return (None, None, None)

    def __set_stored_hashes(self):
        # TODO: Set environment variables ACC_HASH, LEDGER_HASH, POOL_HASH
        hashfile = compose_relative_filepath('file_hashes.dat')
        with open(hashfile, 'wb+') as f:
            pickle.dump((self.acc_hash, self.ledger_hash, self.pool_hash), f)

    def register(self, username: str, password: str):
        if not self.accounts.user_exists(username):
            try:
                priv_key, pub_key = generate_keys()
                user_added = self.accounts.add_user(new_user := User(username,
                                                                     password,
                                                                     encode_keys((priv_key, pub_key),
                                                                                 password)
                                                                     )
                                                    )
                reward_tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                               pub_key,
                               pub_key,
                               REWARD
                               )
                reward_tx.sign(priv_key)
                reward_processed = self.pool.add_tx(reward_tx)
                if user_added and reward_processed:
                    broadcast(new_user)
                    broadcast(reward_tx)
                    self.auto_fill_rewards()
                    self.save_accounts()
                    self.save_pool()
                    return NodeActionResult.SUCCESS
            except Exception as e:
                print(f"Registration failed with exception:\n{e}")
                return NodeActionResult.FAIL

        return NodeActionResult.INVALID

    def login(self, username, password):
        if self.accounts.user_exists(username):
            user = self.accounts.get_user(username)
            if user.authorize(password):
                self.user = user
                self.user_wallet = self.get_user_wallet(user)

                # validation of blocks on chain
                cblock = self.ledger.get_current_block()
                while (cblock is not None and not cblock.was_validated_by(self.user.get_public_key())):
                    self.validate_block(password, cblock)
                    cblock = cblock.previousBlock

                return NodeActionResult.SUCCESS
            else:
                return NodeActionResult.FAIL

        return NodeActionResult.INVALID

    def logout(self):
        self.user = None
        self.user_wallet = None
        return NodeActionResult.SUCCESS

    def validate_block(self, password: str, cblock: CBlock):
        if cblock.state() >= BlockState.MINED and self.user.authorize(password):
            try:
                priv_key, pub_key = self.user.get_rsa_keys(password)
                if cblock.validate_block(priv_key, pub_key):
                    flag = cblock.get_validation_flag(pub_key)
                    broadcast(flag)
                    self.save_ledger()

                    if cblock.state() == BlockState.VALIDATED and len(cblock.validation_flags) == 3:
                        # pay reward to miner upon adding third validation flag
                        reward_tx = Tx(REWARD_VALUE, REWARD_VALUE, 0.0,
                                       pub_key,
                                       decode_public_key(cblock.mined_by),
                                       REWARD
                                       )
                        reward_tx.sign(priv_key)
                        if self.pool.add_tx(reward_tx):
                            broadcast(reward_tx)
                            self.auto_fill_rewards()
                            self.save_pool()

                return NodeActionResult.SUCCESS
            except Exception as e:
                print(f"Validation failed with exception:\n{e}")
                return NodeActionResult.FAIL
        return NodeActionResult.INVALID

    def mine_block(self, miner_password: str):
        if self.curr_block.state() == BlockState.READY and self.user.authorize(miner_password):
            try:
                miner_priv_key, miner_pub_key = self.user.get_rsa_keys(
                    miner_password)
                new: CBlock = self.curr_block.mine(miner_priv_key,
                                                   miner_pub_key
                                                   )
                if new is not self.curr_block and self.curr_block.state() == BlockState.MINED:
                    if self.ledger.add_block(new):
                        # send mined block to network
                        broadcast(self.curr_block)
                        self.save_all()
                        # update current block
                        self.curr_block = self.ledger.get_current_block()
                        # update user wallet
                        self.user_wallet = self.get_user_wallet(self.user)
                        return NodeActionResult.SUCCESS
            except Exception as e:
                print(f"Mining failed with exception:\n{e}")
                return NodeActionResult.FAIL
        return NodeActionResult.INVALID

    def auto_fill_rewards(self):
        head = self.ledger.get_current_block()
        if head.state() <= BlockState.READY:
            pending_txs = self.pool.all_txs()
            rewards = [tx for tx in pending_txs.values() if tx.type == REWARD]

            r = 0

            while len(head.txs) < 10:
                if r < len(rewards):
                    head.add_tx(self.pool.pop_tx(rewards[r].hash.hex()))
                    r += 1
                else:
                    break

            self.save_ledger()
            self.save_pool()

            return NodeActionResult.SUCCESS
        return NodeActionResult.INVALID

    def auto_fill_block(self):
        head = self.ledger.get_current_block()
        if head.state() <= BlockState.READY:
            pending_txs = self.pool.all_txs()
            rewards = [tx for tx in pending_txs.values() if tx.type == REWARD]
            payments = [tx for tx in pending_txs.values() if tx.type == NORMAL]

            r = 0
            p = 0

            while len(head.txs) < 10:
                if r < len(rewards):
                    head.add_tx(self.pool.pop_tx(rewards[r].hash.hex()))
                    r += 1
                elif p < len(payments):
                    head.add_tx(self.pool.pop_tx(payments[p].hash.hex()))
                    p += 1
                else:
                    break

            self.save_ledger()
            self.save_pool()

            return NodeActionResult.SUCCESS
        return NodeActionResult.INVALID

    def move_tx_from_pool_to_current_block(self, tx_hash: str):
        head = self.ledger.get_current_block()
        if len(head.txs) < 10 and head.state() <= BlockState.READY:
            try:
                head.add_tx(self.pool.pop_tx(tx_hash))
                self.save_ledger()
                self.save_pool()
                return NodeActionResult.SUCCESS
            except:
                return NodeActionResult.FAIL
        return NodeActionResult.INVALID

    def move_tx_from_current_block_to_pool(self, tx_hash: str):
        if self.curr_block.state() <= BlockState.READY:
            try:
                if self.curr_block.get_tx(tx_hash).type == NORMAL:
                    self.pool.add_tx(self.curr_block.pop_tx_by_hash(tx_hash))
                    self.save_ledger()
                    self.save_pool()
                    return NodeActionResult.SUCCESS
            except:
                return NodeActionResult.FAIL
        return NodeActionResult.INVALID

    def create_tx(self, input: float, output: float, fee: float, sender_password: str, receiver: rsa.RSAPublicKey):
        if self.user and self.user.authorize(sender_password) and self.user_wallet.available >= input and isclose(input, fsum((output, fee))):
            try:
                sender_priv_key, sender_pub_key = self.user.get_rsa_keys(
                    sender_password)
                tx = Tx(input, output, fee,
                        sender_pub_key,
                        receiver,
                        NORMAL)
                tx.sign(sender_priv_key)
                self.pool.add_tx(tx)
                self.user_wallet = self.get_user_wallet(self.user)
                self.save_pool()
                broadcast(tx)
                return NodeActionResult.SUCCESS
            except:
                return NodeActionResult.FAIL
        return NodeActionResult.INVALID

    def cancel_tx(self, tx_hash: str):
        try:
            self.pool.cancel_tx(tx_hash, self.user.public_key)
            self.user_wallet = self.get_user_wallet(self.user)
            self.save_pool()
            # TODO: broadcast tx cancellation
            return NodeActionResult.SUCCESS
        except:
            return NodeActionResult.FAIL

    def get_user_wallet(self, user: User) -> Wallet:
        processed: dict[str, Tx] = self.ledger.get_txs_by_public_key(
            user.public_key)

        pending: dict[str, Tx] = self.pool.get_txs_by_public_key(
            user.public_key)
        pending.update(
            self.ledger.get_pending_txs_by_public_key(user.public_key))

        incoming = fsum(tx.get_output() for tx in processed.values()
                        if tx.receiver == user.public_key)

        outgoing = fsum(tx.get_input() for tx in processed.values()
                        if tx.sender == user.public_key if tx.type == NORMAL)

        reserved = fsum(tx.get_input() for tx in pending.values()
                        if tx.sender == user.public_key if tx.type == NORMAL)

        fees = self.ledger.get_tx_fees_by_public_key(user.public_key)

        available = fsum((incoming,
                          -outgoing,
                          -reserved,
                          fees)
                         )

        return Wallet(processed,
                      pending,
                      incoming,
                      -outgoing,
                      reserved,
                      fees,
                      available
                      )

    def select_next_block(self):
        if (next_block := self.ledger.get_block_by_id(self.curr_block.id + 1)) is not None:
            self.curr_block = next_block
            return NodeActionResult.SUCCESS
        return NodeActionResult.INVALID

    def select_prev_block(self):
        if (prev_block := self.ledger.get_block_by_id(self.curr_block.id - 1)) is not None:
            self.curr_block = prev_block
            return NodeActionResult.SUCCESS
        return NodeActionResult.INVALID

    # Receive objects from network interface
    def __start_receiving_objects(self):
        # spin thead to receive objects from network interface
        t = Thread(target=self.__receive_objects, daemon=True)
        t.start()

    def __receive_objects(self):
        # TODO: Change print to message queue for GUI
        while True:
            try:
                obj = received_objects.get(block=True, timeout=None)
                match obj:
                    case User() as user:
                        if self.accounts.add_user(user):
                            print(f"Received and added new user: {user}")
                            self.save_accounts()
                            system_messages.put(
                                f"NEW USER REGISTERED: {user.username}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print(f"Received and rejected user: {user}")
                    case Tx() as tx:
                        if tx.type == NORMAL:
                            # lookup user and wallet to check if sender had balance to send tx
                            user = self.accounts.get_user_by_public_key(
                                tx.sender)
                            wallet = self.get_user_wallet(user)
                            if wallet.available >= tx.get_input():
                                if self.pool.add_tx(tx):
                                    # checked if tx is valid ergo signed correctly
                                    print(f"Received new tx: {tx.hash.hex()}")
                                    self.save_pool()
                                    system_messages.put(
                                        f"NEW TX: {tx.hash.hex()}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        elif tx.type == REWARD:
                            if self.pool.add_tx(tx):
                                print(
                                    f"Received new reward tx: {tx.hash.hex()}")
                                self.auto_fill_rewards()
                                self.save_ledger()
                                system_messages.put(
                                    f"NEW REWARD TX: {tx.hash.hex()}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print(f"Received and rejected tx: {tx}")
                    case CBlock() as new_block:
                        if self.ledger.add_mined_block(new_block):
                            print(
                                f"Received new block: {new_block}\nUpdating Tx Pool...")
                            # print(f"Updating txs pool: {new_block.txs}")
                            for key in new_block.txs:
                                if key in self.pool.txs:
                                    self.pool.pop_tx(key)
                            self.curr_block = self.ledger.get_current_block()
                            if self.user is not None:
                                self.user_wallet = self.get_user_wallet(
                                    self.user)
                            self.save_ledger()
                            self.save_pool()
                            system_messages.put(
                                f"NEW BLOCK #{new_block.id} [{new_block.hash}]\nmined by {new_block.mined_by.hex()} @ {new_block.mined_at}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print(f"Received and rejected block: {new_block}")
                    case ValidationFlag() as flag:
                        if self.ledger.get_block_by_id(flag.block_id).add_validation_flag(flag.signature, flag.public_key):
                            print(
                                f"Received new validation flag for block: {flag.block_id} from {flag.public_key.hex()}")
                            self.save_ledger()
                            system_messages.put(
                                f"NEW FLAG: Block #{flag.block_id}\nvalidated by {flag.public_key.hex()}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print(
                                f"Received and rejected validation flag for block: {flag.block_id} from {flag.public_key.hex()}")
                    case NodeSummary() as summary:
                        # Update other node's summary
                        print(
                            f"Received summary from {summary.node_ip}\n{summary}")
                        self.node_summaries[summary.node_ip] = summary

                    case NodeSyncRequest() as request:
                        # no requested items, send own summary
                        if request.block_id is None and request.user is None and request.tx_hash is None:
                            print(
                                f"Received sync request from node: {request}")
                            send_object(request.node_ip, NODE_PORT,
                                        self.__get_summary())

                        elif request.block_id is not None:
                            print(
                                f"Received block request from node: {request}")
                            # send block
                            send_object(request.node_ip, NODE_PORT,
                                        self.ledger.get_block_by_id(request.block_id))
                        elif request.user is not None:
                            print(
                                f"User {request.user} requested by node: {request}")
                            # send user
                            send_object(request.node_ip, NODE_PORT,
                                        self.accounts.get_user(request.user))
                        elif request.tx_hash is not None:
                            print(
                                f"Tx {request.tx_hash} requested by node: {request}")
                            # send tx
                            send_object(request.node_ip, NODE_PORT,
                                        self.pool.get_tx(request))
                    case _:
                        print(
                            f"Received unknown object which was ignored: {obj}")
            except Exception as e:
                print(f"Receiving object failed with error:\n{e}")
                continue

    def __start_syncing_with_peers(self):
        # spin thread to sync with peers
        t = Thread(target=self.__sync_up_with_peers, daemon=True)
        t.start()

    def __sync_up_with_peers(self):
        # entry point to ask peers for their ledger and pool summary, compare them to own, pick best peer, then send requests to update own ledger and pool
        # self.node_summaries.clear()
        sleep(10)  # wait for network interface to start and GUI to load

        print(f"Node {NODE_IP} started syncing with peers...")

        broadcast(NodeSyncRequest())

        own_summary = self.__get_summary()

        while len(self.node_summaries) < len(NODES)-1:
            # wait for all summaries from peers
            sleep(2)

        # pick best peer
        longest_chain = own_summary.node_ip, own_summary.head_id
        missing_users = dict()  # key: username, value = node ip (first found)
        missing_txs = dict()  # key: tx hash, value = node ip (first found)

        for summary in self.node_summaries.values():
            if summary.head_id > longest_chain[1]:
                longest_chain = summary.node_ip, summary.head_id

                for tx_hash in summary.txs:
                    # bring missing txs from longest chain
                    if tx_hash not in own_summary.txs and tx_hash not in missing_txs:
                        missing_txs.update({tx_hash: summary.node_ip})

            for user in summary.users:
                if user not in own_summary.users and user not in missing_users:
                    missing_users.update({user: summary.node_ip})

        # send requests to update own ledger
        if longest_chain[0] != own_summary.node_ip and longest_chain[1] > own_summary.head_id:
            # request blocks from longest chain
            for i in range(own_summary.head_id, longest_chain[1]):
                print(f"Requesting block #{i} from {longest_chain[0]}")
                send_object(longest_chain[0], NODE_PORT,
                            NodeSyncRequest(block_id=i))

        # request missing users
        for user, node_ip in missing_users.items():
            print(f"Requesting user {user} from {node_ip}")
            send_object(node_ip, NODE_PORT, NodeSyncRequest(user=user))

        # request missing txs
        for tx_hash, node_ip in missing_txs.items():
            print(f"Requesting tx {tx_hash} from {node_ip}")
            send_object(node_ip, NODE_PORT, NodeSyncRequest(tx_hash=tx_hash))

        print(f"Node {NODE_IP} finished syncing with peers.")

    def __get_summary(self):
        txs = {tx_hash for tx_hash in self.pool.txs.keys()}
        users = {username for username in self.accounts.users.keys()}
        return NodeSummary(self.ledger.head.id, txs, users)


class NodeSummary(NamedTuple):
    head_id: int
    txs: set[str]
    users: set[str]
    node_ip: str = NODE_IP


class NodeSyncRequest(NamedTuple):
    block_id: int = None
    user: str = None
    tx_hash: str = None
    node_ip: str = NODE_IP
