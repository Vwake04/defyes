import logging
import json

from dataclasses import dataclass, field
from decimal import Decimal
from typing import ClassVar, Dict, List
from web3.contract import Contract
from web3.exceptions import ContractLogicError, ContractCustomError
from web3 import Web3

from defi_protocols.cache import const_call
from defi_protocols.constants import ETHEREUM
from defi_protocols.functions import get_node, get_contract


logger = logging.getLogger(__name__)


class DefiContract:
    ABI = 'MUST_BE_DEFINED'

    def __init__(self, blockchain, address):
        self.blockchain = blockchain
        self.address = address
        self.contract_functions = [func['name'] for func in json.loads(self.ABI)]
        self.node = None
        self.contract = None

        self._func_data = None

    def _update_node_and_contract(self, block):
        if self.node is None or block != self.node._called_with_block:
            self.node = get_node(self.blockchain, block)
            self.contract = self.node.eth.contract(address=self.address, abi=self.ABI)

    def _get_contract_func(self, *args, **kwargs):
        block = kwargs.get('block_identifier', 'latest')
        self._update_node_and_contract(block)
        contract_fun = getattr(self.contract.functions, self._func_data['name'])
        return contract_fun

    def call(self, *args, **kwargs):
        contract_fun = self._get_contract_func(*args, **kwargs)
        return contract_fun(*self._func_data['args'], **self._func_data['kwargs']).call(*args, **kwargs)

    def const_call(self, *args, **kwargs):
        contract_fun = self._get_contract_func(*args, **kwargs)
        return const_call(contract_fun(*self._func_data['args'], **self._func_data['kwargs']))

    def handle_contract_function(self, attr, args, kwargs):
        self._func_data = {'name': attr, 'args': args, 'kwargs': kwargs}
        return self

    def __getattr__(self, attr):
        if attr in self.contract_functions:
            def aux(*args, **kwargs):
                return self.handle_contract_function(attr, args, kwargs)
            return aux
        else:
            raise AttributeError(f"'{self.__class__.__name__}' Object has no attribute '{attr}'")


# Borrow Module
# https://docs.angle.money/angle-borrowing-module/borrowing-module
# https://github.com/AngleProtocol/borrow-contracts/tree/main
class Treasury(DefiContract):
    ABI: str = """[{"inputs":[],\
                    "name":"stablecoin",\
                    "outputs":[{"internalType":"contract IAgToken","name":"","type":"address"}],\
                    "stateMutability":"view","type":"function"},\
                   {"inputs":[{"internalType":"uint256", "name":"","type":"uint256"}],\
                    "name":"vaultManagerList",\
                    "outputs":[{"internalType":"address","name":"","type":"address"}],\
                    "stateMutability":"view","type":"function"\
                   }\
                  ]"""
    ADDRS: Dict = {ETHEREUM: "0x8667DBEBf68B0BFa6Db54f550f41Be16c4067d60"}

    def __init__(self, blockchain) -> None:
        super().__init__(blockchain, self.ADDRS[blockchain])

    @property
    def stable_coin(self):
        return self.stablecoin().const_call()

    def get_all_vault_managers_addrs(self, block) -> List[str]:
        """
        Returns all vault manager addresses from treasury.
        """
        nvault = 0
        vaults = []
        while True:
            try:
                vaults.append(self.vaultManagerList(nvault).const_call())
                nvault += 1
            except ContractLogicError as error:
                if error.message == 'execution reverted':
                    logger.debug('End of vault manager list reachead')
                    break
                else:
                    raise ContracLogicError(error)
        return vaults


class VaultManager(DefiContract):
    ABI: str = """[{"inputs": [{"internalType": "address", "name": "owner", "type": "address"}],\
                    "name": "balanceOf",\
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],\
                    "stateMutability": "view", "type": "function"},\
                   {"inputs":[],\
                    "name":"vaultIDCount",\
                    "outputs":[{"internalType":"uint256","name":"","type":"uint256"}],\
                    "stateMutability":"view","type":"function"},\
                   {"inputs":[{"internalType":"uint256","name":"vaultID","type":"uint256"}],\
                    "name":"ownerOf",\
                    "outputs":[{"internalType":"address","name":"","type":"address"}],\
                    "stateMutability":"view","type":"function"}\
                  ]"""

    def __init__(self, blockchain, address) -> None:
        super().__init__(blockchain, address)

    def has_vaults_owned_by(self, wallet: str, block: int| str) -> bool:
        wallet = Web3.to_checksum_address(wallet)
        return self.balanceOf(wallet).call(block_identifier=block) >= 1


def get_managers_and_vaultcounts(blockchain: str, wallet: str, block: int | str) -> None:
    """
    Returns the list of vault_manager contracts in which the wallet owns at least a Vault.
    """
    wallet = Web3.to_checksum_address(wallet)
    treasury = Treasury(blockchain)

    for vault_addr in treasury.get_all_vault_managers_addrs(block):

        vault_manager = VaultManager(blockchain, vault_addr)

        if vault_manager.has_vaults_owned_by(wallet, block):
            vault_count = vault_manager.vaultIDCount().call(block_identifier=block)
            for nvault in range(vault_count + 1):
                try:
                    if wallet == vault_manager.ownerOf(nvault).call(block_identifier=block):
                        print(nvault)
                except ContractCustomError as error:
                    if error == '0x0c5473ba':
                        pass
                    else:
                        ContractCustomError(error)

