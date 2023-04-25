from defi_protocols.functions import get_node, get_contract, get_decimals, get_logs_web3
from typing import Union
from defi_protocols.util.topic import TopicCreator, AddressHexor
from dataclasses import dataclass, field


POOL_ADDR_V1 = '0xac004b512c33D029cf23ABf04513f1f380B3FD0a'
POOL_ADDR_V2 = '0x204e7371Ade792c5C006fb52711c50a7efC843ed'


@dataclass
class AzuroPools:
    addr: str
    liquidity_added_topic: str = field(init=False)
    liquidity_removed_topic: str = field(init=False)
    version: int = field(init=False)

    def __post_init__(self):
        assert self.addr in [POOL_ADDR_V1, POOL_ADDR_V2], "Wrong Azuro pool address provided"
        if self.addr == POOL_ADDR_V1:
            self.version = 1
            liquidity_added_event = 'LiquidityAdded (index_topic_1 address account, uint256 amount, uint48 leaf)'
            liquidity_removed_event = 'LiquidityRemoved (index_topic_1 address account, index_topic_2 uint48 leaf, uint256 amount)'
        else:
            self.version = 2
            liquidity_added_event = 'LiquidityAdded (index_topic_1 address account, index_topic_2 uint48 leaf, uint256 amount)'
            liquidity_removed_event = 'LiquidityRemoved (index_topic_1 address account, index_topic_2 uint48 leaf, uint256 amount)'

        self.liquidity_added_topic = str(TopicCreator(liquidity_added_event))
        self.liquidity_removed_topic = str(TopicCreator(liquidity_removed_event))


# AZURO token contract ABI
# balanceOf, nodeWithdrawView, ownerOf, tokenOfOwnerByIndex, token, withdrawals, withdrawPayout, withdrawLiquidity
AZURO_POOL_ABI: str = '[{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},\
                        {"inputs":[{"internalType":"uint48","name":"leaf","type":"uint48"}],"name":"nodeWithdrawView","outputs":[{"internalType":"uint128","name":"withdrawAmount","type":"uint128"}],"stateMutability":"view","type":"function"},\
                        {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},\
                        {"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},\
                        {"inputs":[],"name":"token","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},\
                        {"inputs":[{"internalType":"uint48","name":"","type":"uint48"}],"name":"withdrawals","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},\
                        {"inputs":[{"internalType":"uint48","name":"depNum","type":"uint48"},{"internalType":"uint40","name":"percent","type":"uint40"}],"name":"withdrawLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},\
                        {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"withdrawPayout","outputs":[],"stateMutability":"nonpayable","type":"function"}]'


def get_deposit(wallet: str, nftid: int, contract_address: str, block: Union[int, str], blockchain: str, web3=None) -> list:
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    azuro_pool = AzuroPools(contract_address)
    wallet = web3.to_checksum_address(wallet)

    wallethex = str(AddressHexor(wallet))
    nfthex = '0x00000000000000000000000000000000000000000000000000000' + hex(nftid)[2:]

    amount = 0
    add_logs = get_logs_web3(address=azuro_pool.addr,
                             blockchain=blockchain,
                             start_block=0,
                             topics=[azuro_pool.liquidity_added_topic, wallethex],
                             block=block,
                             web3=web3)
    for log in add_logs:
        if azuro_pool.version == 1 and log['data'][-11:] == nfthex[-11:]:
            amount = amount + int(log['data'][:66], 16)
        elif azuro_pool.version == 2:
            amount = amount + int(log['data'], 16)

    remove_logs = get_logs_web3(address=azuro_pool.addr,
                                blockchain=blockchain,
                                start_block=0,
                                topics=[azuro_pool.liquidity_removed_topic, wallethex, nfthex],
                                block=block,
                                web3=web3)
    for log in remove_logs:
        amount = amount - int(log['data'], 16)

    return amount


def underlying(wallet: str, nftid: int, block: Union[int, str], blockchain: str, web3=None, decimals: bool = True, rewards: bool = False) -> list:
    wallet = web3.to_checksum_address(wallet)

    if web3 is None:
        web3 = get_node(blockchain, block=block)
    pool_v1_contract = get_contract(POOL_ADDR_V1, blockchain, web3=web3, abi=AZURO_POOL_ABI, block=block)
    pool_v2_contract = get_contract(POOL_ADDR_V2, blockchain, web3=web3, abi=AZURO_POOL_ABI, block=block)

    balance = 0
    reward = 0
    for contract in [pool_v1_contract, pool_v2_contract]:
        try:
            owner = contract.functions.ownerOf(nftid).call(block_identifier=block)
        except:
            owner = None
        if owner == wallet:
            node_withdraw = contract.functions.nodeWithdrawView(nftid).call(block_identifier=block)
            deposit = get_deposit(wallet, nftid, contract.address, block, blockchain, web3)
            balance += node_withdraw
            reward += node_withdraw - deposit

    token = pool_v1_contract.functions.token().call(block_identifier=block)
    token_decimals = get_decimals(token, blockchain, block=block)
    if decimals:
        balance = balance / (10 ** token_decimals)
        reward = reward / (10 ** token_decimals)

    balance = [token, balance]
    reward = [token, reward]

    balances = [balance]
    if rewards:
        balances = [balance, reward]

    return balances


def underlying_all(wallet: str, block: Union[int, str], blockchain: str, web3=None, decimals: bool = True, rewards: bool = False) -> list:
    if web3 is None:
        web3 = get_node(blockchain, block=block)

    wallet = web3.to_checksum_address(wallet)
    pool_v1_contract = get_contract(POOL_ADDR_V1, blockchain, web3=web3, abi=AZURO_POOL_ABI, block=block)
    assets_pool1 = pool_v1_contract.functions.balanceOf(wallet).call(block_identifier=block)

    pool_v2_contract = get_contract(POOL_ADDR_V2, blockchain, web3=web3, abi=AZURO_POOL_ABI, block=block)
    assets_pool2 = pool_v2_contract.functions.balanceOf(wallet).call(block_identifier=block)

    results = []
    for assets_in_pool in [assets_pool1, assets_pool2]:
        for asset in range(assets_in_pool):
            nftid = pool_v1_contract.functions.tokenOfOwnerByIndex(wallet, asset).call(block_identifier=block)
            results.append([underlying(wallet, nftid, block, blockchain, web3, decimals=decimals, rewards=rewards)][0])

    return results
