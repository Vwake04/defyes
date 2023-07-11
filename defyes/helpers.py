from contextlib import contextmanager, suppress
from functools import wraps
from typing import Any

from web3.exceptions import BadFunctionCallOutput, ContractLogicError

suppressed_error_codes = {-32000, -32015}


@contextmanager
def suppress_error_codes():
    try:
        yield
    except ValueError as e:
        if e.args[0]["code"] not in suppressed_error_codes:
            raise


def call_contract_method(method, block) -> Any | None:
    with suppress(ContractLogicError, BadFunctionCallOutput), suppress_error_codes():
        return method.call(block_identifier=block)


def listify(func):
    """
    Decorator to try to cast the returned iterable into a list.
    Otherwise returns the original returned value on TypeError.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))

    return wrapper
