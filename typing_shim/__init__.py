# type: ignore[attr-defined]
"""Naive shim for mashing typing + typing-extensions into the same module."""
import typing

import sys
from functools import partial
from importlib import import_module
from inspect import getmembers
from itertools import starmap
from operator import contains
from warnings import warn

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    """Return the version string based on lib metadata."""
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

_is_originally_global = partial(contains, list(globals().keys()))


def _is_dunder(name, member):
    """Check if name is a private (dunder) name."""
    if name.startswith("__") and name.endswith("__"):
        return name, member


def _is_private(name, member):
    """Check if passed  private (under) member by name."""
    if not _is_dunder(name, member) and name.startswith("_"):
        return name, member


def _is_public(name, member):
    """Check if name is a public name."""
    if not _is_dunder(name, member) and not _is_private(name, member):
        return name, member


def _get_dunder_members(mod):
    """Yield private (dunder) members  of the module."""
    yield from filter(None, starmap(_is_dunder, getmembers(mod)))


def _get_private_members(mod):
    """Yield private (under) members  of the module."""
    yield from filter(None, starmap(_is_private, getmembers(mod)))


def _get_public_members(mod):
    """Yield public (non-under/dunder) members  of the module."""
    yield from filter(None, starmap(_is_public, getmembers(mod)))


def _adopt_public_members(mod, getmembers_fn=getmembers):
    """Adopt typing members that were not originally in globals."""
    adopted_public_members = set()
    for name, member in getmembers_fn(mod):
        if not _is_originally_global(name):
            adopted_public_members.add(name)
            globals().__setitem__(name, member)
    return adopted_public_members


_typing_reexports_ = set(typing.__all__)
_exports_ = set(_typing_reexports_)

_typing_extensions_reexports_ = set()
_adopted_typing_public_members_ = _adopt_public_members(
    typing, _get_public_members
)
_adopted_typing_extensions_public_members_ = set()
_hidden_typing_public_members_ = set()

if sys.version_info >= (3, 11):
    warn(
        "This package is deprecated for python >= 3.11! You can replace your "
        "typing_shim imports with typing. For compatibility this package will "
        "re-export all typing exports and adopt its public members.",
        DeprecationWarning,
        stacklevel=2,
    )
else:
    typing_extensions = import_module("typing_extensions")
    _typing_extensions_reexports_ = set(typing_extensions.__all__)
    _typing_reexports_ -= _typing_extensions_reexports_
    _exports_ |= _typing_extensions_reexports_
    _adopted_typing_extensions_public_members_ = _adopt_public_members(
        typing_extensions, _get_public_members
    )
    _hidden_typing_public_members_ = (
        _adopted_typing_public_members_
        & _adopted_typing_extensions_public_members_
    )

__all__ = list(_exports_)

_adopted_typing_extensions_public_members_ = list(
    _adopted_typing_extensions_public_members_
)
_adopted_typing_public_members_ = list(_adopted_typing_public_members_)
_hidden_typing_public_members_ = list(_hidden_typing_public_members_)
_typing_extensions_reexports_ = list(_typing_extensions_reexports_)
_typing_reexports_ = list(_typing_reexports_)
