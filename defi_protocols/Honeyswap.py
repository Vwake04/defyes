import math
import logging
from decimal import Decimal

from defi_protocols.functions import get_node, get_contract, get_decimals, get_logs, to_token_amount

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LP Token ABI - decimals, totalSupply, getReserves, balanceOf, token0, token1, kLast
ABI_LPTOKEN = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# EVENT SIGNATURES
# Swap Event Signature
SWAP_EVENT_SIGNATURE = 'Swap(address,uint256,uint256,uint256,uint256,address)'


def get_lptoken_data(lptoken_address, block, blockchain, web3=None):

    if web3 is None:
        web3 = get_node(blockchain, block=block)

    lptoken_data = {}

    lptoken_data['contract'] = get_contract(lptoken_address, blockchain, web3=web3, abi=ABI_LPTOKEN, block=block)

    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()
    lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier=block)
    lptoken_data['token0'] = lptoken_data['contract'].functions.token0().call()
    lptoken_data['token1'] = lptoken_data['contract'].functions.token1().call()
    lptoken_data['reserves'] = lptoken_data['contract'].functions.getReserves().call(block_identifier=block)
    lptoken_data['kLast'] = lptoken_data['contract'].functions.kLast().call(block_identifier=block)

    root_k = (Decimal(lptoken_data['reserves'][0]) * Decimal(lptoken_data['reserves'][1])).sqrt()
    root_k_last = (Decimal(lptoken_data['kLast'])).sqrt()

    if block != 'latest':
        if block < 12108893:
            lptoken_data['virtualTotalSupply'] = lptoken_data['totalSupply']
        else:
            lptoken_data['virtualTotalSupply'] = lptoken_data['totalSupply'] * 6 * root_k / (
                        5 * root_k + root_k_last)
    else:
        lptoken_data['virtualTotalSupply'] = lptoken_data['totalSupply'] * 6 * root_k / (5 * root_k + root_k_last)

    return lptoken_data


# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
def underlying(wallet, lptoken_address, block, blockchain, web3=None, decimals=True):
    result = []

    if web3 is None:
        web3 = get_node(blockchain, block=block)

    wallet = web3.to_checksum_address(wallet)

    lptoken_address = web3.to_checksum_address(lptoken_address)

    lptoken_data = get_lptoken_data(lptoken_address, block, blockchain, web3=web3)

    balance = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier=block)
    pool_balance_fraction = balance / lptoken_data['virtualTotalSupply']

    for n, reserve in enumerate(lptoken_data['reserves']):
        try:
            getattr(lptoken_data['contract'].functions, 'token' + str(n))
        except AttributeError:
            continue

        token_address = lptoken_data['token' + str(n)]
        result.append([token_address,
                       to_token_amount(token_address, reserve, blockchain, web3, decimals) * Decimal(pool_balance_fraction)])

    return result


# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
def pool_balances(lptoken_address, block, blockchain, web3=None, decimals=True):
    balances = []

    if web3 is None:
        web3 = get_node(blockchain, block=block)

    lptoken_address = web3.to_checksum_address(lptoken_address)
    lptoken_contract = get_contract(lptoken_address, blockchain, web3=web3, abi=ABI_LPTOKEN, block=block)
    reserves = lptoken_contract.functions.getReserves().call(block_identifier=block)

    for n, reserve in enumerate(reserves):
        try:
            func = getattr(lptoken_contract.functions, 'token' + str(n))
        except AttributeError:
            continue

        token_address = func().call()
        balances.append([token_address, to_token_amount(token_address, reserve, blockchain, web3, decimals)])

    return balances


def swap_fees(lptoken_address, block_start, block_end, blockchain, web3=None, decimals=True):

    result = {}
    hash_overlap = []

    if web3 is None:
        web3 = get_node(blockchain, block=block_start)

    lptoken_address = web3.to_checksum_address(lptoken_address)

    lptoken_contract = get_contract(lptoken_address, blockchain, web3=web3, abi=ABI_LPTOKEN, block=block_start)

    token0 = lptoken_contract.functions.token0().call()
    token1 = lptoken_contract.functions.token1().call()
    result['swaps'] = []

    decimals0 = get_decimals(token0, blockchain, web3=web3) if decimals else 0
    decimals1 = get_decimals(token1, blockchain, web3=web3) if decimals else 0

    get_logs_bool = True
    block_from = block_start
    block_to = block_end

    swap_event = web3.keccak(text=SWAP_EVENT_SIGNATURE).hex()

    while get_logs_bool:
        swap_logs = get_logs(block_from, block_to, lptoken_address, swap_event, blockchain)

        log_count = len(swap_logs)

        if log_count != 0:
            last_block = int(
                swap_logs[log_count - 1]['blockNumber'][2:len(swap_logs[log_count - 1]['blockNumber'])], 16)

            for swap_log in swap_logs:
                block_number = int(swap_log['blockNumber'][2:len(swap_log['blockNumber'])], 16)

                if swap_log['transactionHash'] in swap_log:
                    continue

                if block_number == last_block:
                    hash_overlap.append(swap_log['transactionHash'])

                if int(swap_log['data'][2:66], 16) == 0:
                    swap_data = {
                        'block': block_number,
                        'token': token1,
                        'amount': Decimal('0.003') * Decimal(int(swap_log['data'][67:130], 16)) / Decimal(10 ** decimals1)
                    }
                else:
                    swap_data = {
                        'block': block_number,
                        'token': token0,
                        'amount': Decimal('0.003') * Decimal(int(swap_log['data'][2:66], 16)) / Decimal(10 ** decimals0)
                    }

                result['swaps'].append(swap_data)

        if log_count < 1000:
            get_logs_bool = False

        else:
            block_from = block_number

    return result
