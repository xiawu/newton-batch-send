#!/usr/bin/env python
# encoding: utf-8

import base58
import json
import sys
import time

from newchain_web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider('https://global.rpc.mainnet.newtonproject.org'))
chain_id = int(w3.net.version)

from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def NewToEth(str):
    return "0x%s" % base58.b58decode_check(str[3:]).hex().lower()[6:]

def loadSendFile(path):
    ret = []
    f = open(path, 'r')
    for line in f.readlines():
        tokens = line.split(',')
        ret.append([tokens[0], tokens[1]])
    f.close()
    return ret

def loadKeystore(path):
    f = open(path, 'r')
    content = f.read()
    ret = json.loads(content)
    f.close()
    return ret

def main():
    keystore_file_path = sys.argv[1]
    send_file_path = sys.argv[2]
    password = sys.argv[3]
    sendList = loadSendFile(send_file_path)

    # read keystore
    keystore = loadKeystore(keystore_file_path)
    w3.eth.account.chain_id=chain_id

    account = w3.eth.account.privateKeyToAccount(w3.eth.account.decrypt(keystore, password))

    from_address = account.address
    nonce = w3.eth.getTransactionCount(from_address)
    for item in sendList:
        to_address = w3.toChecksumAddress(NewToEth(item[0]))
        amount = w3.toWei(item[1], 'ether')
        gas = w3.eth.estimateGas({"from": from_address, "to": to_address, "value": amount})
        gas_price = w3.eth.gasPrice
        signed_txn = account.signTransaction(
            dict(
                nonce=nonce,
                gasPrice=gas_price,
                gas=gas,
                to=to_address,
                value=amount,
                chainId=chain_id)
            )
        w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print("Sent:: from: %s, to: %s, value: %s" % (from_address, to_address, item[1]))
        time.sleep(1)
        nonce += 1

main()
