"""
Autogenerated module. Don't change it manualy. Instead, import its classes into __init__.py or even derive them adding
extra methds.

# Inside __init__.py

from .autogenerated import LiquidityPoolToken, LiquidityPool

# Optionally
class LiquidityPoolToken(LiquidityPoolToken):
    ...
"""
from karpatkit.node import get_node
from web3 import Web3

from defyes.generator import load_abi


class LiquidityPoolToken:
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
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "liquidity_pool_token.json"))

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
    def owner(self) -> str:
        return self.contract.functions.owner().call(block_identifier=self.block)

    @property
    def swap(self) -> str:
        return self.contract.functions.swap().call(block_identifier=self.block)

    @property
    def symbol(self) -> str:
        return self.contract.functions.symbol().call(block_identifier=self.block)

    @property
    def total_supply(self) -> int:
        return self.contract.functions.totalSupply().call(block_identifier=self.block)


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
        node = get_node(blockchain)
        self.contract = node.eth.contract(address=self.address, abi=load_abi(__file__, "liquidity_pool.json"))

    def calculate_current_withdraw_fee(self, user: str) -> int:
        return self.contract.functions.calculateCurrentWithdrawFee(user).call(block_identifier=self.block)

    def calculate_remove_liquidity(self, account: str, amount: int) -> list[int]:
        return self.contract.functions.calculateRemoveLiquidity(account, amount).call(block_identifier=self.block)

    def calculate_remove_liquidity_one_token(self, account: str, token_amount: int, token_index: int) -> int:
        """
        Output: availableTokenAmount
        """
        return self.contract.functions.calculateRemoveLiquidityOneToken(account, token_amount, token_index).call(
            block_identifier=self.block
        )

    def calculate_swap(self, token_index_from: int, token_index_to: int, dx: int) -> int:
        return self.contract.functions.calculateSwap(token_index_from, token_index_to, dx).call(
            block_identifier=self.block
        )

    def calculate_token_amount(self, account: str, amounts: list[int], deposit: bool) -> int:
        return self.contract.functions.calculateTokenAmount(account, amounts, deposit).call(block_identifier=self.block)

    @property
    def get_a(self) -> int:
        return self.contract.functions.getA().call(block_identifier=self.block)

    @property
    def get_a_precise(self) -> int:
        return self.contract.functions.getAPrecise().call(block_identifier=self.block)

    def get_admin_balance(self, index: int) -> int:
        return self.contract.functions.getAdminBalance(index).call(block_identifier=self.block)

    def get_deposit_timestamp(self, user: str) -> int:
        return self.contract.functions.getDepositTimestamp(user).call(block_identifier=self.block)

    def get_token(self, index: int) -> str:
        return self.contract.functions.getToken(index).call(block_identifier=self.block)

    def get_token_balance(self, index: int) -> int:
        return self.contract.functions.getTokenBalance(index).call(block_identifier=self.block)

    def get_token_index(self, token_address: str) -> int:
        return self.contract.functions.getTokenIndex(token_address).call(block_identifier=self.block)

    @property
    def get_virtual_price(self) -> int:
        return self.contract.functions.getVirtualPrice().call(block_identifier=self.block)

    @property
    def swap_storage(self) -> tuple[int, int, int, int, int, int, int, str]:
        """
        Output: initialA, futureA, initialATime, futureATime, swapFee,
        adminFee, defaultWithdrawFee, lpToken
        """
        return self.contract.functions.swapStorage().call(block_identifier=self.block)
