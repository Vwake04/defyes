"""
Autogenerated module. Don't change it manualy. Instead, import its classes into __init__.py or even derive them adding
extra methds.

# Inside __init__.py

from .autogenerated import Gauge, GaugeFactory, GaugeRewardHelper, LiquidityPool, PoolToken, Vault, Vebal, VebalFeeDistributor

# Optionally
class Gauge(Gauge):
    ...
"""
from web3 import Web3

from defyes.cache import const_call
from defyes.generator import load_abi
from defyes.node import get_node


class Gauge:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "gauge.json"))

    def claimable_tokens(self, addr: str) -> int:
        return self.contract.functions.claimable_tokens(addr).call(block_identifier=self.block)

    def claimable_reward(self, _user: str, _reward_token: str) -> int:
        return self.contract.functions.claimable_reward(_user, _reward_token).call(block_identifier=self.block)

    @property
    def reward_count(self) -> int:
        return self.contract.functions.reward_count().call(block_identifier=self.block)

    def reward_tokens(self, arg0: int) -> str:
        return self.contract.functions.reward_tokens(arg0).call(block_identifier=self.block)

    @property
    def reward_contract(self) -> str:
        return self.contract.functions.reward_contract().call(block_identifier=self.block)

    def balance_of(self, arg0: str) -> int:
        return self.contract.functions.balanceOf(arg0).call(block_identifier=self.block)

    @property
    def decimals(self) -> int:
        return const_call(self.contract.functions.decimals())


class GaugeFactory:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "gauge_factory.json"))

    def get_pool_gauge(self, pool: str) -> str:
        return const_call(self.contract.functions.getPoolGauge(pool))


class GaugeRewardHelper:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "gauge_reward_helper.json"))

    def get_pending_rewards(self, gauge: str, user: str, token: str) -> int:
        return self.contract.functions.getPendingRewards(gauge, user, token).call(block_identifier=self.block)


class LiquidityPool:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "liquidity_pool.json"))

    @property
    def get_pool_id(self) -> bytes:
        return const_call(self.contract.functions.getPoolId())

    @property
    def decimals(self) -> int:
        return const_call(self.contract.functions.decimals())

    @property
    def get_actual_supply(self) -> int:
        return self.contract.functions.getActualSupply().call(block_identifier=self.block)

    @property
    def get_virtual_supply(self) -> int:
        return self.contract.functions.getVirtualSupply().call(block_identifier=self.block)

    @property
    def total_supply(self) -> int:
        return self.contract.functions.totalSupply().call(block_identifier=self.block)

    @property
    def get_bpt_index(self) -> int:
        return const_call(self.contract.functions.getBptIndex())

    def balance_of(self, account: str) -> int:
        return self.contract.functions.balanceOf(account).call(block_identifier=self.block)

    @property
    def get_swap_fee_percentage(self) -> int:
        return self.contract.functions.getSwapFeePercentage().call(block_identifier=self.block)

    @property
    def get_rate(self) -> int:
        return self.contract.functions.getRate().call(block_identifier=self.block)

    @property
    def get_scaling_factors(self) -> list[int]:
        return self.contract.functions.getScalingFactors().call(block_identifier=self.block)

    @property
    def pool_id(self) -> bytes:
        return const_call(self.contract.functions.POOL_ID())


class PoolToken:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "pool_token.json"))

    @property
    def decimals(self) -> int:
        return const_call(self.contract.functions.decimals())

    @property
    def get_rate(self) -> int:
        return self.contract.functions.getRate().call(block_identifier=self.block)

    @property
    def underlying_asset_address(self) -> str:
        return self.contract.functions.UNDERLYING_ASSET_ADDRESS().call(block_identifier=self.block)

    @property
    def st_eth(self) -> str:
        return self.contract.functions.stETH().call(block_identifier=self.block)

    @property
    def underlying(self) -> str:
        return self.contract.functions.UNDERLYING().call(block_identifier=self.block)


class Vault:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "vault.json"))

    def get_pool_tokens(self, pool_id: bytes) -> tuple[list[str], list[int], int]:
        # Output: tokens, balances, lastChangeBlock
        return self.contract.functions.getPoolTokens(pool_id).call(block_identifier=self.block)


class Vebal:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "vebal.json"))

    @property
    def token(self) -> str:
        return const_call(self.contract.functions.token())

    def locked(self, arg0: str) -> tuple:
        return self.contract.functions.locked(arg0).call(block_identifier=self.block)


class VebalFeeDistributor:
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
        node = get_node(blockchain, block)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "vebal_fee_distributor.json"))

    def claim_tokens(self, user: str, tokens: list[str]) -> list[int]:
        return self.contract.functions.claimTokens(user, tokens).call(block_identifier=self.block)
