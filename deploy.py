from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

# Solidity source code
install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

# creat json file dump the comiled code in it to make it more readable.
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)
# print(compiled_sol)


# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
# print(abi)

# connecting to ganache
w3 = Web3(Web3.HTTPProvider(os.getenv("RINKEBY_RPC_URL")))
my_address = os.getenv("my_address")
chain_id = 4 # from chainid.network
private_key = os.getenv("testacct_secret")
print(private_key)

#  create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(SimpleStorage)
# get the latest transaction
nonce =w3.eth.getTransactionCount(my_address)
# print(nonce)

# 1. build a transaction
# 2. sign a transaction
# 3. send a transaction
transaction = SimpleStorage.constructor().buildTransaction({
    "chainId": chain_id, 
    "from": my_address, 
    "nonce": nonce,
    "gasPrice": w3.eth.gas_price
    }
)
# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_txn)

# send transaction
print("deploying contract...")
tx_hash =w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("deployed!")
# working with the contract
# we need: contract address, contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call: simulate making the call and getting a return value
# Transact: actually make a state change

# initial value of our favorite number
print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())

print("updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce+1,
    "gasPrice": w3.eth.gas_price,
})
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("updated!")
print(simple_storage.functions.retrieve().call())
