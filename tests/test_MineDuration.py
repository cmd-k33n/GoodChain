import pickle
from time import time, sleep

from Transaction import *
from BlockChain import *
from Signature import generate_keys

MIN_MINING_TIME = 10
MAX_MINING_TIME = 20

if __name__ == "__main__":

    alex_prv, alex_pbc = generate_keys()
    mike_prv, mike_pbc = generate_keys()
    rose_prv, rose_pbc = generate_keys()
    mara_prv, mara_pbc = generate_keys()

    # Valid Transactions
    Tx1 = Tx(5, 5, 0, alex_pbc, rose_pbc)
    Tx1.sign(alex_prv)

    Tx2 = Tx(1, 0.9, 0.1, mike_pbc, rose_pbc)
    Tx2.sign(mike_prv)

    # Valid Transactions
    Tx3 = Tx(3.1, 3, 0.1, rose_pbc, alex_pbc)
    Tx3.sign(rose_prv)

    Tx4 = Tx(2.1, 2, 0.1, mike_pbc, mara_pbc)
    Tx4.sign(mike_prv)

    Tx5 = Tx(REWARD_VALUE, REWARD_VALUE, 0, rose_pbc, rose_pbc, REWARD)
    Tx5.sign(rose_prv)

    Tx6 = Tx(REWARD_VALUE, REWARD_VALUE, 0, mike_pbc, mike_pbc, REWARD)
    Tx6.sign(mike_prv)

    Tx7 = Tx(REWARD_VALUE, REWARD_VALUE, 0, mara_pbc, mara_pbc, REWARD)
    Tx7.sign(mara_prv)

    Tx8 = Tx(10, 8, 2, mike_pbc, mara_pbc)
    Tx8.sign(mike_prv)

    Tx9 = Tx(REWARD_VALUE, REWARD_VALUE, 0, mara_pbc, mara_pbc, REWARD)
    Tx9.sign(mara_prv)

    Tx10 = Tx(REWARD_VALUE, REWARD_VALUE, 0, alex_pbc, alex_pbc, REWARD)
    Tx10.sign(alex_prv)

    # Block "B1": Valid Block with Valid Transactions
    B1 = CBlock(None)
    B1.add_tx(Tx1)
    B1.add_tx(Tx2)
    B1.add_tx(Tx3)
    B1.add_tx(Tx4)
    B1.add_tx(Tx5)
    B1.add_tx(Tx6)
    B1.add_tx(Tx7)
    B1.add_tx(Tx8)
    B1.add_tx(Tx9)
    B1.add_tx(Tx10)

# -------------------------------------------------
    print("Block READY! Start mining...")

    start = time()
    B2 = B1.mine(rose_prv, rose_pbc)
    elapsed = time() - start

    if B2 is not B1 and B1.state() == BlockState.MINED:
        print("Success! Nonce accepted and Block Mined!")
        print(
            f'Accepted Nonce = {str(B1.nonce)} next char limit: {B1.next_char_limit}\n B1 hash: {B1.compute_hash()}')

        print("elapsed time: " + str(elapsed) + " s.")
        if elapsed < MIN_MINING_TIME:
            print("Alarm! Mining is too fast")
        elif elapsed > MAX_MINING_TIME:
            print("Alarm! Mining is too Slow")

    else:
        print("ERROR! Bad nonce")

# -------------------------------------------------

    # validation flags on B1
    B1.validate_block(mike_prv, mike_pbc)
    B1.validate_block(rose_prv, rose_pbc)
    B1.validate_block(mara_prv, mara_pbc)

    if B1.state() == BlockState.VALIDATED:
        print("Success! Block Validated!")
    else:
        print("ERROR! Block validation failed!")

    # Block "B2": Valid Block with Valid Transactions
    B2.add_tx(Tx1)
    B2.add_tx(Tx2)
    B2.add_tx(Tx3)
    B2.add_tx(Tx4)
    B2.add_tx(Tx5)
    B2.add_tx(Tx6)
    B2.add_tx(Tx7)
    B2.add_tx(Tx8)
    B2.add_tx(Tx9)
    B2.add_tx(Tx10)

    # wait for block maturity
    print("Waiting for block maturity...", end="")
    while B2.state() != BlockState.READY:
        sleep(3)
        print(".", end="")

    print("\nBlock maturity reached! Start mining...")

    # mine second block and time it
    # -------------------------------------------------
    start = time()
    B3 = B2.mine(mike_prv, mike_pbc)
    elapsed = time() - start

    if B3 is not B2 and B2.state() == BlockState.MINED:
        print("Success! Nonce accepted and Block Mined!")
        print(
            f'Accepted Nonce = {str(B2.nonce)} next char limit: {B2.next_char_limit}\n B1 hash: {B2.compute_hash()}')

        print("elapsed time: " + str(elapsed) + " s.")
        if elapsed < MIN_MINING_TIME:
            print("Alarm! Mining is too fast")
        elif elapsed > MAX_MINING_TIME:
            print("Alarm! Mining is too Slow")

    else:
        print("ERROR! Bad nonce")

# -------------------------------------------------
