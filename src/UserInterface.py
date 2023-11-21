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

User interface:
■ The application must MINIMALLY have a textual console-based user interface (We're will be implementing a tkinter GUI, also using ttkbootstrap)
■ The user interface must have a menu system to facilitate the operation of the application.
■ The system should always keep users informed about what is going on.
■ User should be able to see the status of and some general information about the system, including:
    the transactions, 
    pool, 
    blockchain, 
    their profile, 
    notifications, 
    recent changes on the system, 
    ongoing actions, etc.
■ The UI should support undo and redo actions when entering data.
■ User should have sufficient control and freedom on the system.
■ Users should not have to wonder whether different words, situations, or actions mean the same thing.
■ There must be reasonable communication with the user regarding the status of the system.
■ Use should have enough contextual help related to the operations of the system.
"""

from __future__ import annotations
from datetime import datetime
from threading import Thread
from queue import Queue

import ttkbootstrap as ttk
from ttkbootstrap.validation import add_regex_validation
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
from ttkbootstrap.dialogs import Messagebox, QueryDialog
from ttkbootstrap.icons import Icon

from src.BlockChain import *
from src.Node import *


class Application(ttk.Window):
    def __init__(self):
        super().__init__(title="GoodChain", themename="darkly")
        # full screen / maximized screen
        self.state('zoomed')
        # self.attributes('-fullscreen', True)
        self.create_widgets()

    def create_widgets(self):
        self.mainframe = MainFrame(self)


class MainFrame(ttk.Frame):
    def __init__(self, master: ttk.Window):
        super().__init__(master, padding=10)
        self.master = master
        self.node: Node = Node()

        self.grid(row=0, column=0, sticky=(N, E, S, W))
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):

        self.top_frame = TopWindow(self)

        self.top_frame.grid(row=0, column=0,
                            rowspan=1,
                            columnspan=3,
                            sticky=(N, E, S, W)
                            )

        self.draw_profilewindow()
        self.draw_blockwindow()
        self.draw_poolwindow()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_rowconfigure(10, weight=1)
        self.grid_rowconfigure(11, weight=1)
        self.grid_rowconfigure(12, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=20, pady=10)

    def update_profilewindow(self):
        self.profile_frame.destroy()
        self.draw_profilewindow()

    def draw_profilewindow(self):
        if self.node.user:
            self.profile_frame = UserViewer(self, self.node)
        else:
            self.profile_frame = Login(self, self.node)

        self.profile_frame.grid(row=1,  column=0,
                                rowspan=11,
                                sticky=(N, E, S, W),
                                padx=20, pady=10
                                )

        self.grid_columnconfigure(0, weight=1)

    def update_blockwindow(self):
        self.block_frame.destroy()
        self.draw_blockwindow()

    def draw_blockwindow(self):
        self.block_frame = BlockViewer(self, self.node)
        self.block_frame.grid(row=1, column=1,
                              rowspan=11,
                              sticky=(N, E, S, W),
                              padx=20, pady=10
                              )

        self.grid_columnconfigure(1, weight=1)

    def update_poolwindow(self):
        self.pool_frame.destroy()
        self.draw_poolwindow()

    def draw_poolwindow(self):
        self.pool_frame = PoolViewer(self, self.node)
        self.pool_frame.grid(row=1, column=2,
                             rowspan=11,
                             sticky=(N, E, S, W),
                             padx=20, pady=10
                             )

        self.grid_columnconfigure(2, weight=1)

    def update_all_windows(self):
        self.update_profilewindow()
        self.update_blockwindow()
        self.update_poolwindow()


class TopWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    # Function to update the clock
    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        # Update the clock every 1 second
        self.master.after(1000, self.update_clock)

    def refresh(self):
        self.master.update_all_windows()

    def quit(self):
        self.master.node.save_all()
        self.master.master.destroy()

    def create_widgets(self):
        # GoodChain banner, system clock, and logo
        self.goodchain_logo = ttk.PhotoImage(data=Icon.warning)
        self.goodchain_logo_label = ttk.Button(self,
                                               image=self.goodchain_logo,
                                               bootstyle=(WARNING, OUTLINE),
                                               command=self.quit
                                               )

        self.goodchain_label = ttk.Label(self,
                                         text="Welcome to GoodChain",
                                         bootstyle=INFO,
                                         font=("Courier New", 32)
                                         )

        self.clock_label = ttk.Label(self,
                                     text="00:00:00",
                                     bootstyle=INFO,
                                     font=("Courier New", 18)
                                     )

        self.separator = ttk.Separator(self,
                                       orient=HORIZONTAL,
                                       bootstyle=LIGHT
                                       )

        self.goodchain_logo_label.grid(row=0, column=0,
                                       sticky=(N, W, S),
                                       padx=20
                                       )
        self.clock_label.grid(row=0, column=2,
                              sticky=(N, E, S),
                              padx=20
                              )
        self.goodchain_label.grid(row=0, column=1,
                                  sticky=(N, S),
                                  padx=20
                                  )
        self.separator.grid(row=1, column=0,
                            columnspan=3,
                            sticky=(N, E, W, S),
                            padx=20
                            )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.update_clock()


class BlockViewer(ttk.Labelframe):
    def __init__(self, master: MainFrame, node: Node):
        super().__init__(master,
                         text="Block Details",
                         labelanchor=N,
                         padding=10,
                         bootstyle=INFO
                         )
        self.master = master
        self.node = node
        self.block = self.node.curr_block
        self.create_widgets()

    def create_widgets(self):
        block_state = self.block.state()

        state_style = (SUCCESS if block_state == BlockState.VALIDATED else
                       (SUCCESS, INVERSE) if block_state == BlockState.MINED else
                       (PRIMARY, INVERSE) if block_state == BlockState.READY else
                       (WARNING, INVERSE))

        state_meter_style = (WARNING if block_state == BlockState.VALIDATED else
                             (SUCCESS) if block_state == BlockState.MINED else
                             PRIMARY if block_state == BlockState.READY else
                             (SECONDARY))

        tx_meter_style = (PRIMARY if len(self.block.txs) < TX_MINIMUM else
                          SUCCESS if len(self.block.txs) < TX_MAXIMUM else
                          DANGER)

        self.block_id_label = ttk.Label(
            master=self,
            text=f"Block ID: {self.block.id}",
            anchor=CENTER,
            bootstyle=state_style
        )

        self.state_label = ttk.Label(
            master=self,
            text=f"State: {self.block.state().name}",
            anchor=CENTER,
            bootstyle=state_style
        )

        self.tx_meter = Meter(master=self,
                              amountused=len(self.block.txs),
                              amounttotal=10,
                              wedgesize=10,
                              bootstyle=tx_meter_style,
                              interactive=False,
                              arcrange=180,
                              arcoffset=180,
                              subtext=f"{len(self.block.txs)}/10 Transactions"
                              )

        self.state_meter = Meter(master=self,
                                 amountused=self.block.state().value,
                                 amounttotal=3,
                                 wedgesize=10,
                                 bootstyle=state_meter_style,
                                 interactive=False,
                                 arcrange=180,
                                 arcoffset=180,
                                 subtext=f"{self.block.state().name}"
                                 )

        self.mine_button = ttk.Button(master=self,
                                      text="Mine",
                                      command=self.try_mine_block,
                                      bootstyle=tx_meter_style if self.node.user is not None else DISABLED
                                      )

        if self.block.previousBlock is not None:
            self.prev_block_button = ttk.Button(master=self,
                                                text=f"[ {self.block.id -1} ] <- Previous Block",
                                                command=self.select_prev_block,
                                                bootstyle=(WARNING, OUTLINE) if self.block.previousBlock.state(
                                                ) <= BlockState.MINED else (SUCCESS, OUTLINE)
                                                )
            self.prev_block_button.grid(row=3, column=0,
                                        sticky=(N, E, S, W))

        if self.block.state() >= BlockState.MINED:
            self.next_block_button = ttk.Button(master=self,
                                                text=f"Next Block ->  [ {self.block.id + 1} ]",
                                                command=self.select_next_block,
                                                bootstyle=(SUCCESS, OUTLINE)
                                                )
            self.next_block_button.grid(row=3, column=1,
                                        sticky=(N, E, S, W))

        self.tx_frame = BlockTxListViewer(self, self.node)

        self.block_id_label.grid(row=0, column=0,
                                 sticky=(N, E, W))

        self.state_label.grid(row=0, column=1,
                              sticky=(N, E, W))

        self.tx_meter.grid(row=2, column=0,
                           sticky=(N, E, S, W))

        self.state_meter.grid(row=2, column=1,
                              sticky=(N, E, S, W))

        self.mine_button.grid(row=1, column=1,
                              columnspan=2,
                              sticky=(N, E, S, W)
                              )

        self.tx_frame.grid(row=5, column=0,
                           columnspan=2,
                           sticky=(N, E, S, W)
                           )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=8)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def try_mine_block(self):
        if self.node.user is not None:
            MineBlockWindow(self, self.node)

    def select_prev_block(self):
        self.node.select_prev_block()
        self.master.update_blockwindow()

    def select_next_block(self):
        self.node.select_next_block()
        self.master.update_blockwindow()


class PoolViewer(ttk.Labelframe):
    def __init__(self, master, node: Node):
        super().__init__(master,
                         text="Live Transaction Pool",
                         labelanchor=N,
                         padding=10,
                         bootstyle=WARNING
                         )
        self.master = master
        self.node = node
        self.create_widgets()

    def create_widgets(self):

        self.tree = PoolTxListViewer(self, self.node)

        self.tree.grid(row=0, column=0,
                       rowspan=10,
                       sticky=(N, E, S, W)
                       )

        self.columnconfigure(0, weight=2)
        self.rowconfigure(0, weight=10)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)


class MineBlockWindow(ttk.Toplevel):

    threadqueue = Queue()

    def __init__(self, master: BlockViewer, node: Node):
        super().__init__(master, size=(600, 350))
        self.master = master
        self.node = node
        self.message = ttk.StringVar(value="")
        self.password = ttk.StringVar(value="")
        self.create_widgets()

    def create_widgets(self):

        container = ttk.Frame(self)
        container.grid(row=0, column=0,
                       sticky=(N, E, S, W),
                       padx=40, pady=40)
        self.grid_columnconfigure(0, weight=1)

        self.main_label = ttk.Label(container,
                                    text=f"Click the START button to begin mining block {self.node.curr_block.id} \n" +
                                    "this will take approximately 10 to 20 seconds.",
                                    bootstyle=INFO,
                                    justify=CENTER
                                    )

        self.input_separator = ttk.Separator(container, orient=HORIZONTAL)

        self.authorization_label = ttk.Label(container,
                                             text="Authorization Required",
                                             bootstyle=WARNING
                                             )

        self.authorization_entry = ttk.Entry(container,
                                             textvariable=self.password,
                                             show="*"
                                             )

        self.start_button = ttk.Button(container,
                                       text='START',
                                       command=self.start_mining,
                                       bootstyle=PRIMARY
                                       )

        self.progressbar = ttk.Floodgauge(container,
                                          maximum=25,
                                          bootstyle=DEFAULT,
                                          mode=INDETERMINATE
                                          )

        self.message_label = ttk.Label(container,
                                       textvariable=self.message,
                                       bootstyle=WARNING,
                                       justify=CENTER
                                       )

        self.main_label.grid(row=0, column=0,
                             columnspan=2,
                             sticky=(N)
                             )
        self.input_separator.grid(row=1, column=0,
                                  columnspan=2,
                                  sticky=(E, W)
                                  )
        self.authorization_label.grid(row=2, column=0,
                                      sticky=(E)
                                      )
        self.authorization_entry.grid(row=2, column=1,
                                      sticky=(W)
                                      )
        self.start_button.grid(row=3, column=0,
                               columnspan=2,
                               sticky=(N, E, S, W)
                               )
        self.progressbar.grid(row=4, column=0,
                              columnspan=2,
                              sticky=(N, E, S, W)
                              )
        self.message_label.grid(row=5, column=0,
                                columnspan=2,
                                sticky=(N)
                                )

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        for child in container.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def start_mining(self):
        self.progressbar.start()
        self.start_button.configure(state=DISABLED)
        result = self.node.mine_block(self.password.get())
        if result == NodeActionResult.SUCCESS:
            self.message.set('Block successfully mined')
            self.progressbar.configure(bootstyle=SUCCESS)
            self.master.master.update_all_windows()
        elif result == NodeActionResult.FAIL:
            self.message.set('Block mining failed')
        else:
            self.message.set('Block mining invalid')
        self.progressbar.stop()
        self.start_button.configure(state=NORMAL)


class TxViewerWindow(ttk.Toplevel):
    def __init__(self, master, tx: Tx):
        super().__init__(master, minsize=(800, 600))
        self.title("Transaction Viewer")
        self.tx = tx
        self.create_widgets()

    def create_widgets(self):
        hash_style = (INFO if self.tx.hash_is_valid() else WARNING)
        tx_style = (SUCCESS if self.tx.is_valid() else DANGER)

        if self.tx.hash is not None:
            self.tx_hash_label = ttk.Label(self,
                                           text=f"Tx Hash: {self.tx.hash.hex()}",
                                           bootstyle=hash_style
                                           )
            self.tx_hash_label.pack()

        self.tx_created_at_label = ttk.Label(self,
                                             text=f"Created At: {self.tx.created_at}",
                                             bootstyle=hash_style
                                             )
        self.tx_created_at_label.pack()

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X)

        type_text = "NORMAL" if self.tx.type == NORMAL else "REWARD"

        self.tx_type_label = ttk.Label(self,
                                       text=f"{type_text}",
                                       bootstyle=tx_style
                                       )
        self.tx_type_label.pack()

        self.tx_input_label = ttk.Label(self,
                                        text=f"Input: {self.tx.input}",
                                        bootstyle=tx_style
                                        )
        self.tx_input_label.pack()

        self.tx_output_label = ttk.Label(self,
                                         text=f"Output: {self.tx.output}",
                                         bootstyle=tx_style
                                         )
        self.tx_output_label.pack()

        self.tx_fee_label = ttk.Label(self,
                                      text=f"Fee: {self.tx.fee}",
                                      bootstyle=tx_style
                                      )
        self.tx_fee_label.pack()

        self.tx_sender_label = ttk.Label(self,
                                         text=f"Sender: {self.tx.sender}",
                                         wraplength=400
                                         )
        self.tx_sender_label.pack()
        self.tx_receiver_label = ttk.Label(self,
                                           text=f"Receiver: {self.tx.receiver}",
                                           wraplength=400
                                           )
        self.tx_receiver_label.pack()

        self.tx_sig_label = ttk.Label(self,
                                      text=f"Signature: {self.tx.sig}",
                                      wraplength=400,
                                      bootstyle=tx_style
                                      )
        self.tx_sig_label.pack()


class PoolTxListViewer(ttk.Frame):
    def __init__(self, master, node: Node):
        super().__init__(master)
        self.master = master
        self.node = node
        self.txs = self.node.pool.all_txs()
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(
            self, columns=[1], selectmode="browse", show="")

        BUTTON_ROW = 0
        TREE_ROW = 2

        if len(self.txs) > 0:
            for tx_hash, tx in self.txs.items():
                self.tree.insert("", "end", id=tx_hash, values=(tx,))

            view_button = ttk.Button(self,
                                     text="View Details",
                                     command=self.open_viewer,
                                     bootstyle=(INFO, OUTLINE)
                                     )
            view_button.grid(row=BUTTON_ROW+1, column=0, sticky=(N, E, S, W))

            move_button = ttk.Button(self,
                                     text="Move to Block",
                                     command=self.move_to_block,
                                     bootstyle=(SUCCESS, OUTLINE))
            move_button.grid(row=BUTTON_ROW, column=0, sticky=(N, E, S, W))

            self.auto_fill_button = ttk.Button(self,
                                               text="Auto Fill",
                                               command=self.auto_fill,
                                               bootstyle=(WARNING, OUTLINE)
                                               )

            self.auto_fill_button.grid(
                row=BUTTON_ROW, column=1, sticky=(N, E, S, W))

            cancel_button = ttk.Button(self,
                                       text="Cancel",
                                       command=self.cancel,
                                       bootstyle=(DANGER, OUTLINE)
                                       )
            cancel_button.grid(row=BUTTON_ROW+1, column=1, sticky=(N, E, S, W))

        self.tree.grid(row=TREE_ROW, column=0,
                       columnspan=2,
                       sticky=(N, E, S, W)
                       )

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # self.columnconfigure(2, weight=1)
        # self.columnconfigure(3, weight=1)
        # self.rowconfigure(BUTTON_ROW, weight=1)
        # self.rowconfigure(BUTTON_ROW+1, weight=1)
        self.grid_rowconfigure(TREE_ROW, weight=10)

    def open_viewer(self):
        tx_hash = self.tree.selection()[0]
        TxViewerWindow(self.master, self.txs[tx_hash])

    def cancel(self):
        tx_hash = self.tree.selection()[0]
        result = self.node.cancel_tx(tx_hash)
        if result == NodeActionResult.SUCCESS:
            Messagebox.ok(title="Success", message="Transaction cancelled")
            self.master.master.update_all_windows()
        elif result == NodeActionResult.FAIL:
            Messagebox.show_error("Cancel failed")
        else:
            Messagebox.show_error("Cancel invalid")

    def move_to_block(self):
        tx_hash = self.tree.selection()[0]
        result = self.node.move_tx_from_pool_to_current_block(tx_hash)
        if result == NodeActionResult.SUCCESS:
            Messagebox.ok(title="Success",
                          message="Transaction moved to Block")
            self.master.master.update_all_windows()
        elif result == NodeActionResult.FAIL:
            Messagebox.show_error("Move failed")
        else:
            Messagebox.show_error("Move invalid")

    def auto_fill(self):
        # auto fill from pool to block
        result = self.node.auto_fill_block()
        if result == NodeActionResult.SUCCESS:
            Messagebox.ok(title="Success",
                          message="Transactions moved to Block")
            self.master.master.update_all_windows()
        elif result == NodeActionResult.FAIL:
            Messagebox.show_error("Auto Fill failed")
        else:
            Messagebox.show_error("Auto Fill invalid")


class BlockTxListViewer(ttk.Frame):
    def __init__(self, master, node: Node):
        super().__init__(master)
        self.master = master
        self.node = node
        self.txs = self.node.curr_block.all_txs()
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(
            self, columns=[1], selectmode="browse", show="")

        if len(self.txs) > 0:
            for tx_hash, tx in self.txs.items():
                self.tree.insert("", "end", id=tx_hash, values=(tx,))

            view_button = ttk.Button(self.master,
                                     text="View Details",
                                     command=self.open_viewer,
                                     bootstyle=(INFO, OUTLINE)
                                     )
            view_button.grid(row=4, column=0, sticky=(N, E, S, W))

            move_to_pool_button = ttk.Button(self.master,
                                             text="Move to Pool",
                                             command=self.move_to_pool,
                                             bootstyle=(WARNING, OUTLINE)
                                             )
            move_to_pool_button.grid(row=4, column=1, sticky=(N, E, S, W))

        self.tree.grid(row=1, column=0,
                       sticky=(N, E, S, W),
                       columnspan=2
                       )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=6)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def open_viewer(self):
        tx_hash = self.tree.selection()[0]
        TxViewerWindow(self.master, self.txs[tx_hash])

    def move_to_pool(self):
        result = self.node.move_tx_from_current_block_to_pool(
            self.tree.selection()[0])
        if result == NodeActionResult.SUCCESS:
            Messagebox.ok(title="Success", message="Transaction moved to Pool")
            self.master.master.update_all_windows()
        elif result == NodeActionResult.FAIL:
            Messagebox.show_error("Move failed")
        else:
            Messagebox.show_error("Move invalid")


class UserTxListViewer(ttk.Frame):
    def __init__(self, master, tx_list: dict[bytes, Tx]):
        super().__init__(master)
        self.master = master
        self.txs = tx_list
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(
            self, columns=[1], selectmode="browse", show="")

        if len(self.txs) > 0:
            for tx_hash, tx in self.txs.items():
                self.tree.insert("", "end", id=tx_hash, values=(tx,))

            view_button = ttk.Button(self,
                                     text="View Details",
                                     command=self.open_viewer,
                                     bootstyle=(INFO, OUTLINE)
                                     )
            view_button.grid(row=1, column=0, sticky=(N, E, S, W))

        self.tree.grid(row=0, column=0, sticky=(N, E, S, W))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=10)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def open_viewer(self):
        tx_hash = self.tree.selection()[0]
        TxViewerWindow(self.master, self.txs[tx_hash])


class CreateTxWindow(ttk.Toplevel):
    def __init__(self, master, node: Node):
        super().__init__(master, minsize=(600, 350))
        self.master = master
        self.node = node

        self.input = ttk.IntVar(value=0)
        self.output = ttk.IntVar(value=0)
        self.fee = ttk.IntVar(value=0)
        self.recipient = ttk.StringVar(value="")
        self.password = ttk.StringVar(value="")

        self.create_widgets()

    def create_widgets(self):
        self.to_label = ttk.Label(self, text="To")
        self.to_entry = ttk.Entry(self, textvariable=self.recipient)
        self.input_label = ttk.Label(self, text="Input")
        self.input_entry = ttk.Entry(self, textvariable=self.input)
        self.output_label = ttk.Label(self, text="Output")
        self.output_entry = ttk.Entry(self, textvariable=self.output)
        self.fee_label = ttk.Label(self, text="Fee")
        self.fee_entry = ttk.Entry(self, textvariable=self.fee)

        self.input_separator = ttk.Separator(self, orient=HORIZONTAL)

        self.authorization_label = ttk.Label(self,
                                             text="Authorization Required",
                                             bootstyle=WARNING
                                             )
        self.authorization_entry = ttk.Entry(self,
                                             textvariable=self.password,
                                             show="*"
                                             )

        self.create_button = ttk.Button(self,
                                        text="Create",
                                        command=self.create_tx
                                        )
        self.cancel_button = ttk.Button(self,
                                        text="Cancel",
                                        command=self.destroy
                                        )

        self.to_label.grid(row=0, column=0, sticky=(N, W, E, S))
        self.to_entry.grid(row=0, column=1, sticky=(N, W, E, S))
        self.input_label.grid(row=1, column=0, sticky=(N, W, E, S))
        self.input_entry.grid(row=1, column=1, sticky=(N, W, E, S))
        self.output_label.grid(row=2, column=0, sticky=(N, W, E, S))
        self.output_entry.grid(row=2, column=1, sticky=(N, W, E, S))
        self.fee_label.grid(row=3, column=0, sticky=(N, W, E, S))
        self.fee_entry.grid(row=3, column=1, sticky=(N, W, E, S))
        self.input_separator.grid(row=4, column=0, columnspan=2,
                                  sticky=(N, W, E, S))
        self.authorization_label.grid(row=5, column=0, sticky=(N, W, E, S))
        self.authorization_entry.grid(row=5, column=1, sticky=(N, W, E, S))
        self.create_button.grid(row=6, column=0, sticky=(N, W, E, S))
        self.cancel_button.grid(row=6, column=1, sticky=(N, W, E, S))

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def create_tx(self):
        # and self.node.user.authorize(self.password.get()):
        if self.node is not None and self.node.user is not None:
            receiver = self.node.accounts.get_user(self.recipient.get())

            result = self.node.create_tx(self.input.get(),
                                         self.output.get(),
                                         self.fee.get(),
                                         self.password.get(),
                                         receiver.get_public_key()
                                         )
            if result == NodeActionResult.SUCCESS:
                Messagebox.ok(title="Success",
                              message="Transaction created successfully")
                self.master.master.update_all_windows()
                self.destroy()
            elif result == NodeActionResult.FAIL:
                Messagebox.show_error("Transaction creation failed")
            else:
                Messagebox.show_error("Transaction invalid")
        else:
            Messagebox.show_error("Authorization failed")


class Login(ttk.Labelframe):
    def __init__(self, master: MainFrame, node: Node):
        super().__init__(master,
                         text="User Details",
                         labelanchor=N,
                         padding=10,
                         bootstyle=WARNING
                         )
        self.master = master
        self.node = node

        self.username = ttk.StringVar()
        self.password = ttk.StringVar()

        self.create_widgets()

    def login(self, username: str, password: str):
        result = self.node.login(username, password)
        if result == NodeActionResult.SUCCESS:
            self.master.update_all_windows()
        else:
            Messagebox.show_error("Login failed!")

    def register(self, username: str, password: str):
        result = self.node.register(username, password)
        if result == NodeActionResult.SUCCESS:
            Messagebox.ok(title="Success", message="Registration successful")
            self.login(username, password)
        elif result == NodeActionResult.FAIL:
            Messagebox.show_error("Registration failed")
        else:
            Messagebox.show_error("Registration invalid")

    def create_widgets(self):
        self.username_label = ttk.Label(self,
                                        text="Username",
                                        bootstyle=PRIMARY,
                                        justify=CENTER
                                        )

        self.username_entry = ttk.Entry(
            self,
            textvariable=self.username,
            validate="focusout",
            validatecommand=lambda: len(self.username.get()) >= 6
        )

        self.password_label = ttk.Label(self,
                                        text="Password",
                                        bootstyle=PRIMARY,
                                        justify=CENTER
                                        )

        self.password_entry = ttk.Entry(
            self,
            textvariable=self.password,
            validate="focusout",
            validatecommand=lambda: len(self.password.get()) >= 12,
            show="*"
        )

        self.login_button = ttk.Button(
            self,
            text="Login",
            bootstyle=PRIMARY,
            command=lambda: self.login(self.username.get(),
                                       self.password.get())
        )

        self.password_entry.bind("<Return>", lambda e: self.login(self.username.get(),
                                                                  self.password.get()))
        # self.bind("<Return>", lambda e: self.login_button.invoke())

        self.register_button = ttk.Button(
            self,
            text="Register",
            bootstyle="primary outline",
            command=lambda: self.register(self.username.get(),
                                          self.password.get())
        )

        self.username_label.grid(row=0, column=0, sticky=(N, W, E, S))
        self.username_entry.grid(row=0, column=1, sticky=(N, W, E, S))

        self.password_label.grid(row=1, column=0, sticky=(N, W, E, S))
        self.password_entry.grid(row=1, column=1, sticky=(N, W, E, S))

        self.login_button.grid(row=2, column=0, columnspan=2, sticky=(W, E))

        self.register_button.grid(row=3, column=0, columnspan=2, sticky=(W, E))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)


class UserViewer(ttk.Labelframe):
    def __init__(self, master: MainFrame, node: Node):
        super().__init__(master,
                         text="User Details",
                         labelanchor=N,
                         padding=10,
                         bootstyle=SUCCESS
                         )
        self.master = master
        self.node = node
        self.user = self.node.user
        self.user_wallet = self.node.user_wallet
        self.create_widgets()

    def show_public_key(self):
        Messagebox.ok(title="Public Key",
                      message=f"Public Key: {self.user.public_key}")

    def show_private_key(self):
        Messagebox.ok(title="Private Key",
                      message=f"Private Key: {self.user.private_key}")

    def logout(self):
        result = self.node.logout()
        if result == NodeActionResult.SUCCESS:
            self.master.update_profilewindow()
        else:
            Messagebox.show_error("Logout failed!")

    def create_tx(self):
        CreateTxWindow(self, self.node)

    def create_widgets(self):
        self.username_label = ttk.Label(self,
                                        text=f"Username: {self.user.username}",
                                        bootstyle=INFO,
                                        font=("Courier New", 16),
                                        justify=CENTER
                                        )
        self.balance_label = ttk.Label(self,
                                       text=f"Balance: {self.user_wallet.available}",
                                       bootstyle=SUCCESS,
                                       font=("Courier New", 12)
                                       )
        self.res_balance_label = ttk.Label(self,
                                           text=f"Reserved: {self.user_wallet.reserved}",
                                           bootstyle=WARNING,
                                           font=("Courier New", 12)
                                           )

        self.tx_summary_label = ttk.Label(self,
                                          text=f"[incoming: {self.user_wallet.incoming} | outgoing: {self.user_wallet.outgoing} | fees: {self.user_wallet.fees}]",
                                          bootstyle=PRIMARY,
                                          font=("Courier New", 10)
                                          )

        self.separator = ttk.Separator(self,
                                       orient=HORIZONTAL,
                                       bootstyle=LIGHT
                                       )

        self.public_key_button = ttk.Button(self,
                                            text="Show Public Key",
                                            command=self.show_public_key,
                                            bootstyle=PRIMARY
                                            )
        self.private_key_button = ttk.Button(self,
                                             text="Show Private Key",
                                             command=self.show_private_key,
                                             bootstyle=PRIMARY
                                             )
        self.create_tx_button = ttk.Button(self,
                                           text="Create Transaction",
                                           command=self.create_tx,
                                           bootstyle=(SUCCESS, OUTLINE)
                                           )
        self.logout_button = ttk.Button(self,
                                        text="Logout",
                                        command=self.logout,
                                        bootstyle=(WARNING, OUTLINE)
                                        )

        txs = self.user_wallet.processed
        txs.update(self.user_wallet.pending)

        self.tx_history = UserTxListViewer(self, txs)

        self.username_label.grid(row=0, column=0,
                                 sticky=(N, W, E, S),
                                 columnspan=2
                                 )

        self.balance_label.grid(row=1, column=0, sticky=(N, W, E, S))
        self.res_balance_label.grid(row=1, column=1, sticky=(N, W, E, S))

        self.tx_summary_label.grid(row=2, column=0,
                                   sticky=(N, W, E, S),
                                   columnspan=2
                                   )

        self.separator.grid(row=3, column=0,
                            columnspan=2,
                            sticky=(N, W, E, S)
                            )

        self.public_key_button.grid(row=4, column=0, sticky=(N, W, E, S))
        self.private_key_button.grid(row=4, column=1, sticky=(N, W, E, S))

        self.create_tx_button.grid(row=5, column=1, sticky=(N, W, E, S))
        self.logout_button.grid(row=5, column=0, sticky=(N, W, E, S))

        self.tx_history.grid(row=6, column=0,
                             columnspan=2,
                             sticky=(N, W, E, S)
                             )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=10)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)
