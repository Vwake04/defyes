"""
Autogenerated module. Don't change it manualy. Instead, import its classes into __init__.py or even derive them adding
extra methds.

# Inside __init__.py

from .autogenerated import Sdtoken, Operator, Gauge

# Optionally
class Sdtoken(Sdtoken):
    ...
"""
from karpatkit.node import get_node
from web3 import Web3

from defyes.generator import load_abi


class Sdtoken:
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
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "sdtoken.json"))

    @property
    def minter(self) -> str:
        return self.contract.functions.minter().call(block_identifier=self.block)

    @property
    def dao(self) -> str:
        return self.contract.functions.DAO().call(block_identifier=self.block)

    @property
    def sd_ve_crv(self) -> str:
        return self.contract.functions.SD_VE_CRV().call(block_identifier=self.block)

    @property
    def ve_crv(self) -> str:
        return self.contract.functions.VE_CRV().call(block_identifier=self.block)

    def allowance(self, owner: str, spender: str) -> int:
        return self.contract.functions.allowance(owner, spender).call(block_identifier=self.block)

    def balance_of(self, account: str) -> int:
        return self.contract.functions.balanceOf(account).call(block_identifier=self.block)

    @property
    def decimals(self) -> int:
        return self.contract.functions.decimals().call(block_identifier=self.block)

    @property
    def name(self) -> str:
        return self.contract.functions.name().call(block_identifier=self.block)

    @property
    def operator(self) -> str:
        return self.contract.functions.operator().call(block_identifier=self.block)

    @property
    def symbol(self) -> str:
        return self.contract.functions.symbol().call(block_identifier=self.block)

    @property
    def total_supply(self) -> int:
        return self.contract.functions.totalSupply().call(block_identifier=self.block)


class Operator:
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
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "operator.json"))

    @property
    def fee_denominator(self) -> int:
        return self.contract.functions.FEE_DENOMINATOR().call(block_identifier=self.block)

    @property
    def sd_ve_crv(self) -> str:
        return self.contract.functions.SD_VE_CRV().call(block_identifier=self.block)

    @property
    def gauge(self) -> str:
        return self.contract.functions.gauge().call(block_identifier=self.block)

    @property
    def governance(self) -> str:
        return self.contract.functions.governance().call(block_identifier=self.block)

    @property
    def incentive_token(self) -> int:
        return self.contract.functions.incentiveToken().call(block_identifier=self.block)

    @property
    def lock_incentive(self) -> int:
        return self.contract.functions.lockIncentive().call(block_identifier=self.block)

    @property
    def locker(self) -> str:
        return self.contract.functions.locker().call(block_identifier=self.block)

    @property
    def minter(self) -> str:
        return self.contract.functions.minter().call(block_identifier=self.block)

    @property
    def token(self) -> str:
        return self.contract.functions.token().call(block_identifier=self.block)


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
        node = get_node(blockchain)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "gauge.json"))

    @property
    def decimals(self) -> int:
        return self.contract.functions.decimals().call(block_identifier=self.block)

    def claimed_reward(self, _addr: str, _token: str) -> int:
        return self.contract.functions.claimed_reward(_addr, _token).call(block_identifier=self.block)

    def claimable_reward(self, _user: str, _reward_token: str) -> int:
        return self.contract.functions.claimable_reward(_user, _reward_token).call(block_identifier=self.block)

    @property
    def sdt(self) -> str:
        return self.contract.functions.SDT().call(block_identifier=self.block)

    @property
    def voting_escrow(self) -> str:
        return self.contract.functions.voting_escrow().call(block_identifier=self.block)

    @property
    def ve_boost_proxy(self) -> str:
        return self.contract.functions.veBoost_proxy().call(block_identifier=self.block)

    @property
    def staking_token(self) -> str:
        return self.contract.functions.staking_token().call(block_identifier=self.block)

    @property
    def decimal_staking_token(self) -> int:
        return self.contract.functions.decimal_staking_token().call(block_identifier=self.block)

    def balance_of(self, arg0: str) -> int:
        return self.contract.functions.balanceOf(arg0).call(block_identifier=self.block)

    @property
    def total_supply(self) -> int:
        return self.contract.functions.totalSupply().call(block_identifier=self.block)

    def allowance(self, arg0: str, arg1: str) -> int:
        return self.contract.functions.allowance(arg0, arg1).call(block_identifier=self.block)

    @property
    def name(self) -> str:
        return self.contract.functions.name().call(block_identifier=self.block)

    @property
    def symbol(self) -> str:
        return self.contract.functions.symbol().call(block_identifier=self.block)

    def working_balances(self, arg0: str) -> int:
        return self.contract.functions.working_balances(arg0).call(block_identifier=self.block)

    @property
    def working_supply(self) -> int:
        return self.contract.functions.working_supply().call(block_identifier=self.block)

    def integrate_checkpoint_of(self, arg0: str) -> int:
        return self.contract.functions.integrate_checkpoint_of(arg0).call(block_identifier=self.block)

    @property
    def reward_count(self) -> int:
        return self.contract.functions.reward_count().call(block_identifier=self.block)

    def reward_tokens(self, arg0: int) -> str:
        return self.contract.functions.reward_tokens(arg0).call(block_identifier=self.block)

    def reward_data(self, arg0: str) -> tuple[str, str, int, int, int, int]:
        """
        Output: token, distributor, period_finish, rate, last_update, integral
        """
        return self.contract.functions.reward_data(arg0).call(block_identifier=self.block)

    def rewards_receiver(self, arg0: str) -> str:
        return self.contract.functions.rewards_receiver(arg0).call(block_identifier=self.block)

    def reward_integral_for(self, arg0: str, arg1: str) -> int:
        return self.contract.functions.reward_integral_for(arg0, arg1).call(block_identifier=self.block)

    @property
    def admin(self) -> str:
        return self.contract.functions.admin().call(block_identifier=self.block)

    @property
    def future_admin(self) -> str:
        return self.contract.functions.future_admin().call(block_identifier=self.block)

    @property
    def claimer(self) -> str:
        return self.contract.functions.claimer().call(block_identifier=self.block)

    @property
    def initialized(self) -> bool:
        return self.contract.functions.initialized().call(block_identifier=self.block)
