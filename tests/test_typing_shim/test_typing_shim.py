"""Tests for typing_shim."""
import typing

from importlib import import_module
from inspect import getmembers

import pytest


def getexports(mod):
    """Return exported members as name, value tuples."""
    if isinstance(mod, str):
        mod = import_module(mod)
    export_names = getattr(mod, "__all__", [])
    if not export_names:
        return []
    return list(filter(lambda kv: kv[0] in export_names, getmembers(mod)))


@pytest.fixture
def import_typing_shim():
    """Return a function to import & return typing_shim module."""
    return lambda: import_module("typing_shim")


def test_import(import_typing_shim):
    """Test basic importability."""
    import_typing_shim()


def test_typing_shim_private_members(import_typing_shim):
    """Assert typing reexport list is provided."""
    shim = import_typing_shim()
    assert getattr(shim, "_adopted_typing_public_members_")
    assert getattr(shim, "_adopted_typing_extensions_public_members_")
    assert getattr(shim, "_hidden_typing_public_members_")
    assert getattr(shim, "_typing_extensions_reexports_")
    assert getattr(shim, "_typing_reexports_")


@pytest.mark.parametrize(("name", "expected"), getexports(typing))
def test_has_typing_member(import_typing_shim, name, expected):
    """Example test with parametrization."""
    typing_shim = import_typing_shim()
    if name not in typing_shim._typing_reexports_:
        pytest.skip("Skipping test for overridden typing member")
    assert name in typing_shim.__all__
    assert getattr(typing_shim, name) is expected


@pytest.mark.parametrize(("name", "expected"), getexports("typing_extensions"))
def test_has_typing_extensions_member(import_typing_shim, name, expected):
    """Example test with parametrization."""
    typing_shim = import_typing_shim()
    assert name in typing_shim.__all__
    assert getattr(typing_shim, name) is expected
