import pytest
from decimal import Decimal

from defi_protocols import Convex
from defi_protocols.functions import get_node, get_contract
from defi_protocols.constants import ETHEREUM, X3CRV_ETH, CRV_ETH, DAI_ETH, USDC_ETH, USDT_ETH, CVX_ETH, LDO_ETH


TEST_BLOCK = 16993460
TEST_WALLET = '0xF929122994E177079c924631bA13Fb280F5CD1f9'
WEB3 = get_node(blockchain=ETHEREUM, block=TEST_BLOCK)

CRV3CRYPTO = '0xc4AD29ba4B3c580e6D59105FFf484999997675Ff'
cDAI_plus_cUSDC = '0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2'
steCRV = '0x06325440D014e39736583c165C2963BA99fAf14E'


def test_get_pool_rewarder():
    x = Convex.get_pool_rewarder(X3CRV_ETH, TEST_BLOCK)
    assert x == '0x689440f2Ff927E1f24c72F1087E1FAF471eCe1c8'


def test_get_rewards():
    rewarder = Convex.get_pool_rewarder(CRV3CRYPTO, TEST_BLOCK)
    rw_contract = get_contract(rewarder, ETHEREUM,
                               web3=WEB3, abi=Convex.ABI_REWARDS,
                               block=TEST_BLOCK)
    wallet = '0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C'
    x = Convex.get_rewards(WEB3, rw_contract, wallet, TEST_BLOCK,
                           ETHEREUM, decimals=False)
    assert x == [CRV_ETH, Decimal('2628703131997023420479')]


# @pytest.mark.parametrize('lp_token', [CRV3CRYPTO, cDAI_plus_cUSDC, steCRV])
@pytest.mark.parametrize('lp_token', [steCRV])
# @pytest.mark.parametrize('wallet', [TEST_WALLET,
@pytest.mark.parametrize('wallet', ['0x849D52316331967b6fF1198e5E32A0eB168D039d'])
                                    # '0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C', 
                                    # '0x849D52316331967b6fF1198e5E32A0eB168D039d'])
def test_get_extra_rewards(lp_token, wallet):
    rewarder = Convex.get_pool_rewarder(lp_token, TEST_BLOCK)
    rw_contract = get_contract(rewarder, ETHEREUM,
                               web3=WEB3, abi=Convex.ABI_REWARDS,
                               block=TEST_BLOCK)
    x = Convex.get_extra_rewards(WEB3, rw_contract, wallet, TEST_BLOCK,
                                 ETHEREUM, decimals=False)
    assert x == [[LDO_ETH, Decimal('1680694318843318519229')]]


def test_get_cvx_mint_amount():
    x = Convex.get_cvx_mint_amount(WEB3, False, TEST_BLOCK, ETHEREUM, decimals=False)
    assert x == [CVX_ETH, Decimal('0')]


def test_get_all_rewards():
    x = Convex.get_all_rewards(TEST_WALLET, X3CRV_ETH, TEST_BLOCK, ETHEREUM,
                               WEB3, False, None)
    assert x == [[CRV_ETH, Decimal('0')],
                 [CVX_ETH, Decimal('0')]]


def test_get_locked():
    x = Convex.get_locked(TEST_WALLET, TEST_BLOCK, ETHEREUM,
                          WEB3, reward=False, decimals=False)
    assert x == [[CVX_ETH, Decimal('0')]]


def test_get_staked():
    x = Convex.get_staked(TEST_WALLET, TEST_BLOCK, ETHEREUM,
                          WEB3, reward=False, decimals=False)
    assert x == [[CVX_ETH, Decimal('0')]]


def test_underlying():
    x = Convex.underlying(TEST_WALLET, X3CRV_ETH, TEST_BLOCK, ETHEREUM,
                          WEB3, reward=True, decimals=False,
                          no_curve_underlying=False)
    assert x == \
        [[DAI_ETH, Decimal('0')],
         [USDC_ETH, Decimal('0')],
         [USDT_ETH, Decimal('0')],
         [CRV_ETH, Decimal('0')],
         [CVX_ETH, Decimal('0')]]


def test_pool_balances():
    x = Convex.pool_balances(X3CRV_ETH, TEST_BLOCK, ETHEREUM,
                             WEB3, decimals=False)
    assert x == [[DAI_ETH, Decimal('165857824629254122209119338')],
                 [USDC_ETH, Decimal('175604425510732')],
                 [USDT_ETH, Decimal('92743777795510')]]


@pytest.mark.skip(reason="Takes too long")
def test_update_db():
    data = Convex.update_db(save_to="/dev/null")
    assert data
