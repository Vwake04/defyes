from web3 import Web3


class Addr(str):
    # TODO: Maybe move chain to Addr
    def __new__(cls, addr: int | str, *args, **kwargs):
        if isinstance(addr, str):
            cs_addr = Web3.to_checksum_address(addr)
            if cs_addr != addr:
                raise cls.ChecksumError(f"Provided {addr=!r} differs from expected {cs_addr!r}")
            s = addr
        else:
            s = Web3.to_checksum_address(addr)
        return super().__new__(cls, s)

    class ChecksumError(ValueError):
        pass


infura_url = "https://mainnet.infura.io/v3/38e708fc0d1c40fa8e56b52c4c7e9eb2"

web3 = Web3(Web3.HTTPProvider(infura_url))

abi = '[{"inputs":[],"name":"liquidityPools","outputs":[{"internalType":"contract Token[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"}]'
address = "0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB"

contract = web3.eth.contract(address=address, abi=abi)
liquidity_pools = contract.functions.liquidityPools().call()

# network info
ni_abi = '[{"inputs":[{"internalType":"contract Token","name":"pool","type":"address"}],"name":"poolToken","outputs":[{"internalType":"contract IPoolToken","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract Token","name":"pool","type":"address"},{"internalType":"uint256","name":"poolTokenAmount","type":"uint256"}],"name":"withdrawalAmounts","outputs":[{"components":[{"internalType":"uint256","name":"totalAmount","type":"uint256"},{"internalType":"uint256","name":"baseTokenAmount","type":"uint256"},{"internalType":"uint256","name":"bntAmount","type":"uint256"}],"internalType":"struct WithdrawalAmounts","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bnt","outputs":[{"internalType":"contractToken","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'
ni_address = "0x8E303D296851B320e6a697bAcB979d13c9D6E760"

ni_contract = web3.eth.contract(address=ni_address, abi=ni_abi)

bnt = ni_contract.functions.bnt().call()
print(bnt)


pool_tokens = []
for pool in liquidity_pools[:2]:
    pool_token = ni_contract.functions.poolToken(pool).call()
    print(f"Pool: {pool}, Pool Token: {pool_token}")
    pool_tokens.append(pool_token)

withdrawal_amount = ni_contract.functions.withdrawalAmounts(pool, 100).call()

pool_abi = '[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"reserveToken","outputs":[{"internalType":"contract Token","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'
BNT_TOKEN = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"

pool_contract = web3.eth.contract(address=pool_token, abi=pool_abi)
c = Web3.to_checksum_address("0x849d52316331967b6ff1198e5e32a0eb168d039d")
print(c)
balance = pool_contract.functions.balanceOf(c).call()
print(f"Balance: {balance}")
reserve_token = pool_contract.functions.reserveToken().call()
print(f"Reserve Token: {reserve_token}")

