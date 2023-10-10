from typing import Iterator, NamedTuple

from web3 import Web3

from defyes.constants import Chain
from defyes.types import Addr, Token, TokenAmount

from .autogenerated import BaseVault


class StEthVolatilityVault(BaseVault):
    """
    stETH Volatility Vault

    This is a low-risk strategy that focuses on ETH accumulation. It invests in Lido and uses part of Lido's yield to
    set up strangles weekly. It accumulates more ETH whenever the price goes up and when it goes down.
    """

    default_addresses: dict[str, str] = {
        Chain.ETHEREUM: Addr("0x463F9ED5e11764Eb9029762011a03643603aD879"),
        Chain.GOERLI: Addr("0x626bC69e52A543F8dea317Ff885C9060b8ebbbf5"),
    }


class EthphoriaVault(BaseVault):
    """
    ETHphoria Vault

    This is a low-risk strategy that focuses on ETH accumulation. The vault stakes ETH in Lido and uses all weekly yield
    to buy one-week ETH call options on a weekly basis. It accumulates more ETH whenever the price goes up. It is a way
    to go long on ETH without risking the principal.
    """

    default_addresses: dict[str, str] = {
        Chain.ETHEREUM: Addr("0x5FE4B38520e856921978715C8579D2D7a4d2274F"),
    }


class UsdcFudVault(BaseVault):
    """
    USDC FUD Vault

    This is a low-risk strategy that focuses on hedging against market crashes. The vault invests USDC in Aave and uses
    all weekly yield to buy one-week ETH put options on a weekly basis. It accumulates more USDC whenever the price goes
    down.
    """

    default_addresses: dict[str, str] = {
        Chain.ETHEREUM: Addr("0x287f941aB4B5AaDaD2F13F9363fcEC8Ee312a969"),
    }


vault_classes = {
    StEthVolatilityVault,
    EthphoriaVault,
    UsdcFudVault,
}


class VaultAssetShare(NamedTuple):
    valut: BaseVault
    asset_amount: TokenAmount
    share_amount: TokenAmount


def underlyings_holdings(
    wallet: Addr, block_id="latest", blockchain: Chain = Chain.ETHEREUM
) -> Iterator[VaultAssetShare]:
    for vault_class in vault_classes:
        vault = vault_class(blockchain, block_id)
        asset = Token.get_instance(vault.asset, vault.blockchain, vault.block)
        share = Token.get_instance(vault.address, vault.blockchain, vault.block)
        yield VaultAssetShare(
            vault,
            TokenAmount.from_teu(vault.assets_of(wallet), asset),
            TokenAmount.from_teu(vault.balance_of(wallet), share),
        )


def get_protocol_data(
    wallet: Addr, block: int | str, blockchain: Chain = Chain.ETHEREUM, decimals: bool = True
) -> dict:
    wallet = Web3.to_checksum_address(wallet)

    positions = {
        vault.address: {
            "underlyings": [asset_amount.as_dict(decimals)],
            "holdings": [share_amount.as_dict(decimals)],
        }
        for vault, asset_amount, share_amount in underlyings_holdings(wallet, block_id=block, blockchain=blockchain)
        if asset_amount != 0 or share_amount != 0
    }

    return {
        "blockchain": blockchain,
        "block_id": block,
        "protocol": "Pods",
        "version": 0,
        "wallet": wallet,
        "decimals": decimals,
        "positions": positions,
        "positions_key": "vault_address",
        "financial_metrics": {},
    }
