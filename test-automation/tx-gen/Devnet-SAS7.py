#!/usr/bin/env python3

import time
import sys
import logging
import datetime
from multiprocessing.pool import ThreadPool

import harmony_transaction_generator as tx_gen
from harmony_transaction_generator import account_manager
from harmony_transaction_generator import analysis
import pyhmy
from pyhmy import cli
from pyhmy import util

verbose = True

tx_gen.set_config({
    "AMT_PER_TXN": [1, 1],  # The random range for each transaction in the transaction-generation
    "NUM_SRC_ACC": 1,  # The number of possible source accounts for all transactions
    "NUM_SNK_ACC": 10,  # The number of possible destination / sink accounts for all transaction
    "MAX_TXN_GEN_COUNT": 1,  # The upper bound of the number generated transaction, regardless of if `stop` is called
    "ONLY_CROSS_SHARD": False,  # If true, forces source and destination shards to be different
    "ESTIMATED_GAS_PER_TXN": 1e-3,  # The estimated gas, hardcoded
    "INIT_SRC_ACC_BAL_PER_SHARD": 1.1,  # The initial balance for EVERY source account
    "TXN_WAIT_TO_CONFIRM": 60,  # The timeout when a transaction is sent (only used in setup related functions)
    "MAX_THREAD_COUNT": 8,  # Max thread is recommended to be less than your v-core count
    "ENDPOINTS": [  # Endpoints for all transaction, index i = shard i
        "https://api.s0.pga.hmny.io",
        "https://api.s1.pga.hmny.io",
        "https://api.s2.pga.hmny.io"
    ],
    "SRC_SHARD_WEIGHTS": [  # Adjust the likelihood that shard i (i = index) gets chosen to be the source shard
        0,
        1,
        0
    ],
    "SNK_SHARD_WEIGHTS": [  # Adjust the likelihood that shard i (i = index) gets chosen to be the source shard
        0,
        1,
        0
    ],
    "CHAIN_ID": "devnet",  # The chain id for all transaction, should be devnet if not localnet.
    "REFUND_ACCOUNT": "one1j9hwh7vqz94dsk06q4h9hznr4wlr3x5zup6wz3",  # All refunds will be sent to this account
})

def setup():
    assert hasattr(pyhmy, "__version__")
    assert pyhmy.__version__.major == 20, "wrong pyhmy version"
    assert pyhmy.__version__.minor == 1, "wrong pyhmy version"
    assert pyhmy.__version__.micro >= 6, "wrong pyhmy version, update please"
    env = cli.download("./bin/hmy", replace=False)
    cli.environment.update(env)
    cli.set_binary("./bin/hmy")


def log_writer(interval):
    while True:
        tx_gen.write_all_logs()
        time.sleep(interval)


if __name__ == "__main__":
    setup()
    if verbose:
        tx_gen.Loggers.general.logger.addHandler(logging.StreamHandler(sys.stdout))
        tx_gen.Loggers.balance.logger.addHandler(logging.StreamHandler(sys.stdout))
        tx_gen.Loggers.transaction.logger.addHandler(logging.StreamHandler(sys.stdout))
        tx_gen.Loggers.report.logger.addHandler(logging.StreamHandler(sys.stdout))

    log_writer_pool = ThreadPool(processes=1)
    log_writer_pool.apply_async(log_writer, (5,))

    config = tx_gen.get_config()
    # funding accounts should be loaded if not in CLI's keystore.
    # this means that if we have the fauce keys in the keystore, we do not need the `load_accounts` call.
    tx_gen.load_accounts("./devnet_keys", "", fast_load=True)
    #print("CLI's account keystore: ", cli.get_accounts_keystore())  # Allows you to check if correct keys were added
    source_accounts = tx_gen.create_accounts(config["NUM_SRC_ACC"], "src_acc")
    sink_accounts = tx_gen.create_accounts(config["NUM_SNK_ACC"], "snk_acc")
    tx_gen.fund_accounts(source_accounts)
    # Funding is faster if there are more loaded / present faucet accounts in the CLI's keystore

    tx_gen_pool = ThreadPool(processes=1)
    start_time = datetime.datetime.utcnow()  # MUST be utc
    tx_gen_pool.apply_async(lambda: tx_gen.start(source_accounts, sink_accounts))
    time.sleep(30)
    tx_gen.stop()
    end_time = datetime.datetime.utcnow()  # MUST be utc
    tx_gen.return_balances(source_accounts)
    tx_gen.return_balances(sink_accounts)
    tx_gen.remove_accounts(source_accounts)
    tx_gen.remove_accounts(sink_accounts)
    time.sleep(25)
    report = analysis.verify_transactions(tx_gen.Loggers.transaction.filename, start_time, end_time)
    print(report)
    assert report["received-transaction-report"]["successful-transactions-total"] == 10
    assert report["received-transaction-report"]["failed-transactions-total"] == 0