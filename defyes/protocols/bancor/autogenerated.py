"""
Autogenerated module. Don't change it manualy. Instead, import its classes into __init__.py or even derive them adding
extra methds.

# Inside __init__.py

from .autogenerated import BancorPool, BancorNetwork, BancorNetworkInfo

class BancorNetwork(BancorNetwork):
    ...
"""
from karpatkit.node import get_node
from web3 import Web3

from defyes.generator import load_abi


class BancorNetwork:
    default_addresses: dict[str, str]

    def __init__(self, blockchain: str, block: int, address: str | None = None) -> None:
        self.block = block
        self.blockchain = blockchain
        if address:
            self.address = Web3.to_checksum_address(address)
        else:
            try:
                self.address = self.default_addresses[blockchain]
            except AttributeError as e:
                raise ValueError("No default_addresses defined when trying to guess the address.") from e
            except KeyError as e:
                raise ValueError(
                    f"{blockchain!r} not defined in default_addresses when trying to guess the address."
                ) from e
        node = get_node(blockchain)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "network.json"))

    @property
    def liquidity_pools(self) -> list[str]:
        return self.contract.functions.liquidityPools().call(block_identifier=self.block)


class BancorNetworkInfo:
    default_addresses: dict[str, str]

    def __init__(self, blockchain: str, block: int, address: str | None = None) -> None:
        self.block = block
        self.blockchain = blockchain
        if address:
            self.address = Web3.to_checksum_address(address)
        else:
            try:
                self.address = self.default_addresses[blockchain]
            except AttributeError as e:
                raise ValueError("No default_addresses defined when trying to guess the address.") from e
            except KeyError as e:
                raise ValueError(
                    f"{blockchain!r} not defined in default_addresses when trying to guess the address."
                ) from e
        node = get_node(blockchain)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "network_info.json"))

    @property
    def pool_token(self, pool_address: str) -> str:
        return self.contract.functions.poolToken(pool_address).call(block_identifier=self.block)
    
    def withdrawal_amounts(self, pool_address: str, pool_token_amount: int) -> tuple[int, int, int]:
        return self.contract.functions.withdrawalAmounts(pool_address, pool_token_amount).call(block_identifier=self.block)
 

class BancorPool:
    default_addresses: dict[str, str]

    def __init__(self, blockchain: str, block: int, address: str | None = None) -> None:
        self.block = block
        self.blockchain = blockchain
        if address:
            self.address = Web3.to_checksum_address(address)
        else:
            try:
                self.address = self.default_addresses[blockchain]
            except AttributeError as e:
                raise ValueError("No default_addresses defined when trying to guess the address.") from e
            except KeyError as e:
                raise ValueError(
                    f"{blockchain!r} not defined in default_addresses when trying to guess the address."
                ) from e
        node = get_node(blockchain)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "pool.json"))

    def balance_of(self, owner: str) -> int:
        return self.contract.functions.balanceOf(owner).call(block_identifier=self.block)

    @property
    def reserve_token(self) -> str:
        return self.contract.functions.reserveToken().call(block_identifier=self.block)