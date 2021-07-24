# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = (
    "AdvancedIterator",
    "ColoredString",
    "Colorize",
    "Debug",
    "derive",
    "Functor",
    "has_trait",
    "impl",
    "Just",
    "Maybe",
    "Nothing",
    "trait",
)

from . import derive, has_trait, impl, trait
from .traits.colored import ColoredString, Colorize
from .traits.debug import Debug
from .traits.functor import Functor, Just, Maybe, Nothing
from .traits.iterator import AdvancedIterator

# combo impls


@impl(Debug >> ColoredString)
@impl(Debug >> Maybe)
class DebugRepr:
    def fmt(self):
        return repr(self)
