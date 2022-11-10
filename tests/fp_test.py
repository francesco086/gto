from unittest.mock import patch

from gto.git_utils import _turn_args_into_kwargs, args_to_kwargs


def _print_hello(name: str):
    print(f"Hello {name}")


# @args_to_kwargs
# def print_hello(name: str):
#     _print_hello(name)

print_hello = args_to_kwargs(_print_hello)


def test_args_to_kwargs_is_called():
    with patch("gto.git_utils._turn_args_into_kwargs") as spy_args_to_kwargs:
        spy_args_to_kwargs.side_effect = _turn_args_into_kwargs
        print_hello("Bob")
    spy_args_to_kwargs.assert_called_once()
    spy_args_to_kwargs.assert_called_once_with(_print_hello, ("Bob",), {"name": "Bob"})
