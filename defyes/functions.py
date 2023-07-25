import calendar
import json
import logging
import math
import re
from contextlib import suppress
from datetime import datetime
from decimal import Decimal

import requests
from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, BadFunctionCallOutput, ContractLogicError

from defyes.cache import cache_call, const_call
from defyes.constants import (
    ABI_TOKEN_SIMPLIFIED,
    API_ARBITRUM_GETABI,
    API_ARBITRUM_GETLOGS,
    API_ARBITRUM_TOKENTX,
    API_ARBITRUM_TXLIST,
    API_AVALANCHE_GETABI,
    API_AVALANCHE_GETLOGS,
    API_AVALANCHE_TOKENTX,
    API_AVALANCHE_TXLIST,
    API_BINANCE_GETABI,
    API_BINANCE_GETLOGS,
    API_BINANCE_TOKENTX,
    API_BINANCE_TXLIST,
    API_BLOCKSCOUT_GETABI,
    API_BLOCKSCOUT_GETTOKENCONTRACT,
    API_ETHERSCAN_GETABI,
    API_ETHERSCAN_GETCONTRACTCREATION,
    API_ETHERSCAN_GETLOGS,
    API_ETHERSCAN_TOKENTX,
    API_ETHERSCAN_TXLIST,
    API_ETHPLORER_GETTOKENINFO,
    API_FANTOM_GETABI,
    API_FANTOM_GETLOGS,
    API_FANTOM_TOKENTX,
    API_FANTOM_TXLIST,
    API_GNOSISSCAN_GETABI,
    API_GNOSISSCAN_GETLOGS,
    API_GNOSISSCAN_TOKENTX,
    API_GNOSISSCAN_TXLIST,
    API_GOERLI_GETABI,
    API_GOERLI_GETLOGS,
    API_GOERLI_TOKENTX,
    API_GOERLI_TXLIST,
    API_KOVAN_GETABI,
    API_KOVAN_GETLOGS,
    API_KOVAN_TOKENTX,
    API_KOVAN_TXLIST,
    API_OPTIMISM_GETABI,
    API_OPTIMISM_GETLOGS,
    API_OPTIMISM_TOKENTX,
    API_OPTIMISM_TXLIST,
    API_POLYGONSCAN_GETABI,
    API_POLYGONSCAN_GETLOGS,
    API_POLYGONSCAN_TOKENTX,
    API_POLYGONSCAN_TXLIST,
    API_ROPSTEN_GETABI,
    API_ROPSTEN_GETLOGS,
    API_ROPSTEN_TOKENTX,
    API_ROPSTEN_TXLIST,
    IMPLEMENTATION_SLOT_EIP_1967,
    IMPLEMENTATION_SLOT_UNSTRUCTURED,
    TESTNET_HEADER,
    Address,
    APIKey,
    BlockToTime,
    Chain,
    TimeToBlock,
)
from defyes.helpers import suppress_error_codes
from defyes.node import get_node

logger = logging.getLogger(__name__)


def latest_not_in_params(args):
    return "latest" not in args


# CUSTOM EXCEPTIONS
class BlockchainError(Exception):
    pass


class GetNodeIndexError(Exception):
    """ """

    pass


class abiNotVerified(Exception):
    """ """

    def __init__(self, message="Contract source code not verified") -> None:
        self.message = message
        super().__init__(self.message)


def to_token_amount(
    token_address: str, amount: int | Decimal, blockchain: str, web3: Web3, decimals: bool = True
) -> Decimal:
    # This function provides support for correctly rounded decimal floating point arithmetic.
    decimals = get_decimals(token_address, blockchain=blockchain, web3=web3) if decimals else 0
    return amount / Decimal(10**decimals)


def last_block(blockchain, web3=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    return web3.eth.block_number


def timestamp_to_date(timestamp, utc=0):
    return datetime.utcfromtimestamp(timestamp + 3600 * utc).strftime("%Y-%m-%d %H:%M:%S")


@cache_call()
def timestamp_to_block(timestamp, blockchain) -> int:
    data = None
    block_getter = TimeToBlock(blockchain)
    while data is None:
        data = block_getter.make_request(timestamp)
    return int(data)


def date_to_timestamp(datestring, utc=0):
    #   localTimestamp = math.floor(time.mktime(datetime.strptime(datestring,'%Y-%m-%d %H:%M:%S').timetuple()) + 3600 * utc)
    utc_timestamp = math.floor(
        calendar.timegm(datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S").timetuple()) - 3600 * utc
    )

    return utc_timestamp


def date_to_block(datestring, blockchain, utc=0) -> int:
    """
    Returns the block number of a specified date.

    The date can be a string (in the format '%Y-%m-%d %H:%M:%S') or a datetime object. UTC is asumed as timezone.
    An example datestring: '2023-02-20 18:30:00'.
    """
    if hasattr(datestring, "utctimetuple"):
        timestamp = calendar.timegm(datestring.utctimetuple())
    else:
        timestamp = date_to_timestamp(datestring, utc=utc)

    return timestamp_to_block(timestamp, blockchain)


@cache_call()
def block_to_timestamp(block, blockchain):
    data = None
    if isinstance(block, str):
        if block == "latest":
            return math.floor(datetime.now().timestamp())

    time_getter = BlockToTime(blockchain)
    while data is None:
        data = time_getter.make_request(block)

    return int(data)


def block_to_date(block, blockchain, utc=0):
    return timestamp_to_date(block_to_timestamp(block, blockchain), utc=utc)


def get_blocks_per_year(blockchain):
    current_block = last_block(blockchain)
    ts = math.floor(datetime.now().timestamp()) - (3600 * 24 * 365)
    block = timestamp_to_block(ts, blockchain)

    block_delta = current_block - block

    return block_delta


# ERC20 TOKENS
# token_info
@cache_call()
def token_info(token_address, blockchain):  # NO ESTÁ Chain.POLYGON
    if blockchain.lower() == Chain.ETHEREUM:
        data = requests.get(API_ETHPLORER_GETTOKENINFO % (token_address, APIKey.ETHPLORER)).json()

    elif blockchain.lower() == Chain.GNOSIS:
        data = requests.get(API_BLOCKSCOUT_GETTOKENCONTRACT % token_address).json()["result"]

    return data


def balance_of(address, contract_address, block, blockchain, web3=None, decimals=True) -> Decimal:
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    address = Web3.to_checksum_address(address)
    contract_address = Web3.to_checksum_address(contract_address)

    balance = 0
    if contract_address == Address.ZERO:
        balance = web3.eth.get_balance(address, block)
    else:
        token_contract = web3.eth.contract(address=contract_address, abi=json.loads(ABI_TOKEN_SIMPLIFIED))
        try:
            balance = token_contract.functions.balanceOf(address).call(block_identifier=block)
        except ContractLogicError:
            pass

    return to_token_amount(contract_address, balance, blockchain, web3, decimals)


def total_supply(
    token_address: str, block: int | str, blockchain: str, web3: Web3 = None, decimals: bool = True
) -> Decimal:
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    token_address = Web3.to_checksum_address(token_address)

    token_contract = web3.eth.contract(address=token_address, abi=json.loads(ABI_TOKEN_SIMPLIFIED))
    total_supply_v = token_contract.functions.totalSupply().call(block_identifier=block)

    return to_token_amount(token_address, total_supply_v, blockchain, web3, decimals)


def get_decimals(token_address, blockchain, web3=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    token_address = Web3.to_checksum_address(token_address)

    if token_address == Address.ZERO or token_address == Address.E:
        decimals = 18
    else:
        token_contract = web3.eth.contract(address=token_address, abi=json.loads(ABI_TOKEN_SIMPLIFIED))
        decimals = const_call(token_contract.functions.decimals())

    return decimals


def get_symbol(token_address, blockchain, web3=None, block="latest") -> str:
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    token_address = Web3.to_checksum_address(token_address)

    if token_address == Address.ZERO or token_address == Address.E:
        if blockchain is Chain.ETHEREUM or blockchain is Chain.OPTIMISM or blockchain is Chain.ARBITRUM:
            symbol = "ETH"
        elif blockchain is Chain.POLYGON:
            symbol = "MATIC"
        elif blockchain is Chain.GNOSIS:
            symbol = "Chain.GNOSIS"
        elif blockchain is Chain.FANTOM:
            symbol = "FTM"
        elif blockchain is Chain.AVALANCHE:
            symbol = "AVAX"
        elif blockchain is Chain.BINANCE:
            symbol = "BNB"
    else:
        symbol = infer_symbol(web3, blockchain, token_address)

        if not isinstance(symbol, str):
            symbol = symbol.hex()
            symbol = bytes.fromhex(symbol).decode("utf-8").rstrip("\x00")

    return symbol


def infer_symbol(web3, blockchain, token_address):
    contract = web3.eth.contract(address=token_address, abi=ABI_TOKEN_SIMPLIFIED)
    for method_name in ("symbol", "SYMBOL"):
        with suppress(ContractLogicError, BadFunctionCallOutput), suppress_error_codes():
            return const_call(getattr(contract.functions, method_name)())

    abi = get_contract_abi(token_address, blockchain)
    contract = web3.eth.contract(address=token_address, abi=abi)
    with suppress(ContractLogicError, BadFunctionCallOutput), suppress_error_codes():
        return const_call(contract.functions.symbol())

    raise ValueError(f"Token {token_address} has no symbol()")


# CONTRACTS AND ABIS
@cache_call()
def get_contract_abi(contract_address, blockchain):
    data = None

    while data is None:
        if blockchain == Chain.ETHEREUM:
            data = requests.get(API_ETHERSCAN_GETABI % (contract_address, APIKey.ETHERSCAN)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.POLYGON:
            data = requests.get(API_POLYGONSCAN_GETABI % (contract_address, APIKey.POLSCAN)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.GNOSIS:
            data = requests.get(API_GNOSISSCAN_GETABI % (contract_address, APIKey.GNOSISSCAN)).json()["result"]
            if data == "Contract source code not verified":
                data = requests.get(API_BLOCKSCOUT_GETABI % contract_address).json()["result"]
                if data == "Contract source code not verified":
                    raise abiNotVerified

        elif blockchain == Chain.BINANCE:
            data = requests.get(API_BINANCE_GETABI % (contract_address, APIKey.BINANCE)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.AVALANCHE:
            data = requests.get(API_AVALANCHE_GETABI % (contract_address, APIKey.AVALANCHE)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.FANTOM:
            data = requests.get(API_FANTOM_GETABI % (contract_address, APIKey.FANTOM)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.OPTIMISM:
            data = requests.get(API_OPTIMISM_GETABI % (contract_address, APIKey.OPTIMISM)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.ARBITRUM:
            data = requests.get(API_ARBITRUM_GETABI % (contract_address, APIKey.ARBITRUM)).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.ROPSTEN:
            data = requests.get(
                API_ROPSTEN_GETABI % (contract_address, APIKey.ETHERSCAN), headers=TESTNET_HEADER
            ).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.KOVAN:
            data = requests.get(API_KOVAN_GETABI % (contract_address, APIKey.ETHERSCAN), headers=TESTNET_HEADER).json()[
                "result"
            ]
            if data == "Contract source code not verified":
                raise abiNotVerified

        elif blockchain == Chain.GOERLI:
            data = requests.get(
                API_GOERLI_GETABI % (contract_address, APIKey.ETHERSCAN), headers=TESTNET_HEADER
            ).json()["result"]
            if data == "Contract source code not verified":
                raise abiNotVerified

    return data


def get_contract(contract_address, blockchain, web3=None, abi=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    contract_address = Web3.to_checksum_address(contract_address)

    if abi is None:
        try:
            abi = get_contract_abi(contract_address, blockchain)
            return web3.eth.contract(address=contract_address, abi=abi)
        except abiNotVerified:
            logger.exception("ABI not verified")
            return None
    else:
        return web3.eth.contract(address=contract_address, abi=abi)


def get_contract_proxy_abi(contract_address, abi_contract_address, blockchain, web3=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    address = Web3.to_checksum_address(contract_address)

    try:
        abi = get_contract_abi(abi_contract_address, blockchain)
        return web3.eth.contract(address=address, abi=abi)
    except abiNotVerified as Ex:
        logger.exception(Ex)
        return None


def search_proxy_impl_address(contract_address, blockchain, web3=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain)

    proxy_impl_address = Address.ZERO

    contract_address = Web3.to_checksum_address(contract_address)

    # OpenZeppelins' EIP-1967 - Example in mainnet: 0xE95A203B1a91a908F9B9CE46459d101078c2c3cb
    proxy_impl_address = Web3.to_hex(
        web3.eth.get_storage_at(contract_address, IMPLEMENTATION_SLOT_EIP_1967, block_identifier=block)
    )
    proxy_impl_address = Web3.to_checksum_address("0x" + proxy_impl_address[-40:])

    # OpenZeppelins' EIP-1167 - Example in GC: 0x793fAF861a78B07c0C8c0ed1450D3919F3473226)
    if proxy_impl_address == Address.ZERO:
        bytecode = web3.eth.get_code(contract_address, block_identifier=block).hex()
        if bytecode[2:22] == "363d3d373d3d3d363d73" and bytecode[62:] == "5af43d82803e903d91602b57fd5bf3":
            proxy_impl_address = Web3.to_checksum_address("0x" + bytecode[22:62])

    # Custom proxy implementation (similar to EIP-1167) -
    # Examples: mainnet: 0x09cabEC1eAd1c0Ba254B09efb3EE13841712bE14 / GC: 0x7B7DA887E0c18e631e175532C06221761Db30A24
    if proxy_impl_address == Address.ZERO:
        bytecode = web3.eth.get_code(contract_address, block_identifier=block).hex()
        if bytecode[2:32] == "366000600037611000600036600073" and bytecode[72:] == "5af41558576110006000f3":
            proxy_impl_address = Web3.to_checksum_address("0x" + bytecode[32:72])

    # OpenZeppelins' Unstructured Storage proxy pattern - Example: USDC in mainnet (0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48)
    if proxy_impl_address == Address.ZERO:
        proxy_impl_address = Web3.to_hex(
            web3.eth.get_storage_at(contract_address, IMPLEMENTATION_SLOT_UNSTRUCTURED, block_identifier=block)
        )
        proxy_impl_address = Web3.to_checksum_address("0x" + proxy_impl_address[-40:])

    # OpenZeppelins' EIP-897 DelegateProxy - Examples: stETH in mainnet (0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84)
    # It also includes the custom proxy implementation of the Comptroller: 0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B
    if proxy_impl_address == Address.ZERO:
        contract = get_contract(contract_address, blockchain, web3=web3)
        if contract is not None:
            for func in [obj for obj in contract.abi if obj["type"] == "function"]:
                name = str(func["name"].lower())
                if "implementation" in name:
                    output_types = [output["type"] for output in func["outputs"]]
                    if output_types == ["address"]:
                        try:
                            proxy_impl_address_func = getattr(contract.functions, func["name"])
                            proxy_impl_address = proxy_impl_address_func().call(block_identifier=block)
                            break
                        except Exception as e:
                            if type(e) == ContractLogicError or type(e) == BadFunctionCallOutput:
                                continue

    # Custom proxy implementation (used by Safes) - Example: mainnet: 0x4F2083f5fBede34C2714aFfb3105539775f7FE64
    if proxy_impl_address == Address.ZERO:
        contract_custom_abi = get_contract(
            contract_address,
            Chain.ETHEREUM,
            abi='[{"inputs":[{"internalType":"uint256","name":"offset","type":"uint256"},{"internalType":"uint256","name":"length","type":"uint256"}],"name":"getStorageAt","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"}]',
        )
        try:
            proxy_impl_address = Web3.to_hex(contract_custom_abi.functions.getStorageAt(0, 1).call())
            proxy_impl_address = Web3.to_checksum_address("0x" + proxy_impl_address[-40:])
        except Exception as e:
            if type(e) == ContractLogicError or type(e) == BadFunctionCallOutput:
                pass

    return proxy_impl_address


def get_abi_function_signatures(contract_address, blockchain, web3=None, abi_address=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain)

    contract_address = Web3.to_checksum_address(contract_address)

    if abi_address is None:
        proxy_impl_address = search_proxy_impl_address(contract_address, blockchain, web3=web3, block=block)
        contract = get_contract_proxy_abi(contract_address, proxy_impl_address, blockchain, web3=web3)
    else:
        contract = get_contract_proxy_abi(contract_address, abi_address, blockchain, web3=web3, block=block)

    if contract is not None:
        abi = contract.abi

        functions = []
        for func in [obj for obj in abi if obj["type"] == "function"]:
            name = func["name"]
            input_types = [input["type"] for input in func["inputs"]]

            function = {}
            function["name"] = name
            function["signature"] = "{}{}".format(name, "(")
            function["inline_signature"] = "{}{}".format(name, "(")
            function["components"] = []
            function["stateMutability"] = func["stateMutability"]

            i = 0
            for input_type in input_types:
                if input_type == "tuple":
                    function["components"] = [component["type"] for component in func["inputs"][i]["components"]]
                    function["inline_signature"] += "({})".format(",".join(function["components"]))
                else:
                    function["inline_signature"] += input_type
                    function["components"].append(input_type)

                function["signature"] += input_type

                if i < len(input_types) - 1:
                    function["signature"] += ","
                    function["inline_signature"] += ","

                i += 1

            function["signature"] += ")"
            function["inline_signature"] += ")"

            functions.append(function)

        return functions

    return None


def get_data(contract_address, function_name, parameters, blockchain, web3=None, abi_address=None, block="latest"):
    if web3 is None:
        web3 = get_node(blockchain)

    contract_address = Web3.to_checksum_address(contract_address)

    contract = None

    if abi_address is None:
        contract = get_contract(contract_address, blockchain, web3=web3)

        if contract is not None:
            try:
                getattr(contract.functions, function_name)
            except ABIFunctionNotFound:
                # If the contract does not have the function, it checks if there is a proxy implementation
                proxy_impl_address = search_proxy_impl_address(contract_address, blockchain, web3=web3, block=block)

                if proxy_impl_address != Address.ZERO:
                    contract = get_contract_proxy_abi(contract_address, proxy_impl_address, blockchain, web3=web3)
    else:
        contract = get_contract_proxy_abi(contract_address, abi_address, blockchain, web3=web3)

    try:
        return contract.encodeABI(fn_name=function_name, args=parameters)
    except Exception:
        logger.exception("Exception in get_data")
        return None


# ACCOUNTS
@cache_call(filter=latest_not_in_params)
def get_token_tx(token_address, contract_address, block_start, block_end, blockchain):
    data = None

    if blockchain == Chain.ETHEREUM:
        data = requests.get(
            API_ETHERSCAN_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.ETHERSCAN)
        ).json()["result"]

    elif blockchain == Chain.POLYGON:
        data = requests.get(
            API_POLYGONSCAN_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.POLSCAN)
        ).json()["result"]

    elif blockchain == Chain.GNOSIS:
        data = requests.get(
            API_GNOSISSCAN_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.GNOSISSCAN)
        ).json()["result"]

    elif blockchain == Chain.BINANCE:
        data = requests.get(
            API_BINANCE_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.BINANCE)
        ).json()["result"]

    elif blockchain == Chain.AVALANCHE:
        data = requests.get(
            API_AVALANCHE_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.AVALANCHE)
        ).json()["result"]

    elif blockchain == Chain.FANTOM:
        data = requests.get(
            API_FANTOM_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.FANTOM)
        ).json()["result"]

    elif blockchain == Chain.OPTIMISM:
        data = requests.get(
            API_OPTIMISM_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.OPTIMISM)
        ).json()["result"]

    elif blockchain == Chain.ARBITRUM:
        data = requests.get(
            API_ARBITRUM_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.ARBITRUM)
        ).json()["result"]

    elif blockchain == Chain.ROPSTEN:
        data = requests.get(
            API_ROPSTEN_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.ETHERSCAN)
        ).json()["result"]

    elif blockchain == Chain.KOVAN:
        data = requests.get(
            API_KOVAN_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.ETHERSCAN)
        ).json()["result"]

    elif blockchain == Chain.GOERLI:
        data = requests.get(
            API_GOERLI_TOKENTX % (token_address, contract_address, block_start, block_end, APIKey.ETHERSCAN)
        ).json()["result"]

    return data


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_tx_list
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@cache_call(filter=latest_not_in_params)
def get_tx_list(contract_address, block_start, block_end, blockchain):
    data = None

    if blockchain == Chain.ETHEREUM:
        data = requests.get(API_ETHERSCAN_TXLIST % (contract_address, block_start, block_end, APIKey.ETHERSCAN)).json()[
            "result"
        ]

    elif blockchain == Chain.POLYGON:
        data = requests.get(API_POLYGONSCAN_TXLIST % (contract_address, block_start, block_end, APIKey.POLSCAN)).json()[
            "result"
        ]

    elif blockchain == Chain.GNOSIS:
        data = requests.get(
            API_GNOSISSCAN_TXLIST % (contract_address, block_start, block_end, APIKey.GNOSISSCAN)
        ).json()["result"]

    elif blockchain == Chain.BINANCE:
        data = requests.get(API_BINANCE_TXLIST % (contract_address, block_start, block_end, APIKey.BINANCE)).json()[
            "result"
        ]

    elif blockchain == Chain.AVALANCHE:
        data = requests.get(API_AVALANCHE_TXLIST % (contract_address, block_start, block_end, APIKey.AVALANCHE)).json()[
            "result"
        ]

    elif blockchain == Chain.FANTOM:
        data = requests.get(API_FANTOM_TXLIST % (contract_address, block_start, block_end, APIKey.FANTOM)).json()[
            "result"
        ]

    elif blockchain == Chain.OPTIMISM:
        data = requests.get(API_OPTIMISM_TXLIST % (contract_address, block_start, block_end, APIKey.OPTIMISM)).json()[
            "result"
        ]

    elif blockchain == Chain.ARBITRUM:
        data = requests.get(API_ARBITRUM_TXLIST % (contract_address, block_start, block_end, APIKey.ARBITRUM)).json()[
            "result"
        ]

    elif blockchain == Chain.ROPSTEN:
        data = requests.get(API_ROPSTEN_TXLIST % (contract_address, block_start, block_end, APIKey.ETHERSCAN)).json()[
            "result"
        ]

    elif blockchain == Chain.KOVAN:
        data = requests.get(API_KOVAN_TXLIST % (contract_address, block_start, block_end, APIKey.ETHERSCAN)).json()[
            "result"
        ]

    elif blockchain == Chain.GOERLI:
        data = requests.get(API_GOERLI_TXLIST % (contract_address, block_start, block_end, APIKey.ETHERSCAN)).json()[
            "result"
        ]

    return data


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_contract_creation
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@cache_call(filter=latest_not_in_params)
def get_contract_creation(contract_addresses, blockchain):
    data = None

    if blockchain == Chain.ETHEREUM:
        data = requests.get(API_ETHERSCAN_GETCONTRACTCREATION % (contract_addresses, APIKey.ETHERSCAN)).json()["result"]

    return data


# LOGS
def get_block_intervals(blockchain, block_start, block_end, block_interval):
    block_interval = block_end if block_interval is None else block_interval

    if block_end == "latest":
        web3 = get_node(blockchain)
        block_end = web3.eth.block_number

    n_blocks = list(range(block_start, block_end + 1, block_interval))
    n_blocks += [] if ((block_end - block_start) / block_interval) % 1 == 0 else [block_end]

    return list(zip(n_blocks[:-1], n_blocks[1:]))


@cache_call()
def get_logs_http(block_start, block_end, address, topic0, blockchain, **kwargs):
    # Returns only the first 1000 results
    KEYS_WHITELIST = [
        "topic1",
        "topic2",
        "topic3",
        "topic0_1_opr",
        "topic0_2_opr",
        "topic0_3_opr",
        "topic1_2_opr",
        "topic1_3_opr" "topic2_3_opr",
    ]
    data = None
    optional_parameters = ""
    for key, value in kwargs.items():
        if key in KEYS_WHITELIST and value:
            optional_parameters += f"&{key}={value}"

    if blockchain == Chain.ETHEREUM:
        data = requests.get(
            API_ETHERSCAN_GETLOGS % (block_start, block_end, address, topic0, APIKey.ETHERSCAN) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.POLYGON:
        data = requests.get(
            API_POLYGONSCAN_GETLOGS % (block_start, block_end, address, topic0, APIKey.POLSCAN) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.GNOSIS:
        data = requests.get(
            API_GNOSISSCAN_GETLOGS % (block_start, block_end, address, topic0, APIKey.GNOSISSCAN) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.AVALANCHE:
        data = requests.get(
            API_AVALANCHE_GETLOGS % (block_start, block_end, address, topic0, APIKey.AVALANCHE) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.BINANCE:
        data = requests.get(
            API_BINANCE_GETLOGS % (block_start, block_end, address, topic0, APIKey.BINANCE) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.FANTOM:
        data = requests.get(
            API_FANTOM_GETLOGS % (block_start, block_end, address, topic0, APIKey.FANTOM) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.OPTIMISM:
        data = requests.get(
            API_OPTIMISM_GETLOGS % (block_start, block_end, address, topic0, APIKey.OPTIMISM) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.ARBITRUM:
        data = requests.get(
            API_ARBITRUM_GETLOGS % (block_start, block_end, address, topic0, APIKey.ARBITRUM) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.ROPSTEN:
        data = requests.get(
            API_ROPSTEN_GETLOGS % (block_start, block_end, address, topic0, APIKey.ETHERSCAN) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.KOVAN:
        data = requests.get(
            API_KOVAN_GETLOGS % (block_start, block_end, address, topic0, APIKey.ETHERSCAN) + optional_parameters
        ).json()["result"]

    elif blockchain == Chain.GOERLI:
        data = requests.get(
            API_GOERLI_GETLOGS % (block_start, block_end, address, topic0, APIKey.ETHERSCAN) + optional_parameters
        ).json()["result"]

    return data


# get_logs_web3
def get_logs_web3(
    address: str,
    blockchain: str,
    block_start: int | str = None,
    block_end: int | str = None,
    topics: list = None,
    block_hash: str = None,
    web3: Web3 = None,
) -> dict:
    # FIXME: Add documentation
    if web3 is None:
        web3 = get_node(blockchain, block=block_end)

    address = Web3.to_checksum_address(address)
    try:
        params = {"address": address, "fromBlock": block_start, "toBlock": None, "topics": topics}
        if block_hash is not None:
            params.update({"blockHash": block_hash})
        logs = web3.eth.get_logs(params)

        if not isinstance(block_end, str) and block_end is not None:
            for n in range(len(logs)):
                if logs[n]["blockNumber"] > block_end:
                    logs = logs[:n]
                    break
    except ValueError as error:
        error_info = error.args[0]

        if error_info["code"] == -32005:  # error code in infura
            block_interval = int(error_info["data"]["to"], 16) - int(error_info["data"]["from"], 16)
        elif error_info["code"] == -32602:  # error code in alchemy
            blocks = [int(block, 16) for block in re.findall(r"0x[0-9a-fA-F]+", error_info["message"])]
            block_interval = blocks[1] - blocks[0]
        else:
            raise ValueError(error_info)

        logger.debug(
            f"Web3.eth.get_logs: query returned more than 10000 results. Trying with a {block_interval} block range."
        )
        logs = []
        params = {"address": address, "topics": topics}
        if block_hash is not None:
            params.update({"blockHash": block_hash})

        for from_block, to_block in get_block_intervals(blockchain, block_start, block_end, block_interval):
            params.update({"fromBlock": from_block, "toBlock": to_block})
            logs += web3.eth.get_logs(params)

    return logs


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_block_samples(start_date, samples, blockchain, end_date="latest", utc=0, dates=False):
    start_timestamp = date_to_timestamp(start_date, utc=utc)
    if end_date == "latest":
        end_timestamp = math.floor(datetime.now().timestamp())
    else:
        end_timestamp = date_to_timestamp(end_date, utc=utc)

    period = int((end_timestamp - start_timestamp) / (samples - 1))

    timestamps = [start_timestamp + i * period for i in range(samples)]

    dates_strings = [
        datetime.utcfromtimestamp(timestamp + 3600 * utc).strftime("%Y-%m-%d %H:%M:%S") for timestamp in timestamps
    ]

    blocks = [timestamp_to_block(timestamps[i], blockchain) for i in range(samples)]

    if dates is True:
        return [blocks, dates_strings]
    else:
        return blocks


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def is_archival(endpoint) -> bool:
    """
    Checks whether a node is an archival node or a full node.

    :param str endpoint: The node's RPC endpoint to analyse
    :return: True if the node is archival, False if it isn't
    """

    web3 = Web3(Web3.HTTPProvider(endpoint))

    try:
        web3.eth.get_balance("0x849D52316331967b6fF1198e5E32A0eB168D039d", block_identifier=1)
    except ValueError:
        return False
    return True
