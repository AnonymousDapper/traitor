# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = (
    "derive",
    "has_trait",
    "impl",
    "trait",
    "ColoredString",
    "Colorize",
    "Debug",
    "Functor",
    "Just",
    "Maybe",
    "Nothing",
    "From",
    "Into",
    "AdvancedIterator",
)

from . import derive, has_trait, impl, trait
from .traits.colored import ColoredString, Colorize
from .traits.debug import Debug
from .traits.functor import Functor, Just, Maybe, Nothing
from .traits.into import From, Into
from .traits.iterator import AdvancedIterator

# combo impls


@impl(Debug >> ColoredString)
@impl(Debug >> Maybe)
class DebugRepr:
    def fmt(self):
        return repr(self)
