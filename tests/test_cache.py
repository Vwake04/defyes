from unittest.mock import Mock
from defi_protocols.cache import cache_call, const_call, TemporaryCache

def test_cache_decorator():
    with TemporaryCache():
        centinel = Mock()

        @cache_call(exclude_args=['c', 'd'])
        def f(a, b, c, d = None):
            centinel()
            return a + b + c

        assert 3 == f(1, 2, 0)
        assert centinel.call_count == 1
        assert 3 == f(1, 2, 0)
        assert 3 == f(1, 2, 0, 'foo')
        assert 3 == f(1, 2, 3, d='foo')
        assert centinel.call_count == 1 # only called once

def test_const_call():
    with TemporaryCache():
        centinel = Mock()
        web3_contract_function = Mock()
        web3_contract_function.address = '0xcafe'
        web3_contract_function.args = tuple()
        web3_contract_function.kwargs = dict()
        web3_contract_function.function_identifier = 'decimals'
        web3_contract_function.web3._network_name = 'ethereum'

        def _call():
            centinel()
        web3_contract_function.call = _call

        const_call(web3_contract_function)
        assert centinel.call_count == 1
        const_call(web3_contract_function)
        assert centinel.call_count == 1  # only called once