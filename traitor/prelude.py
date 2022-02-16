# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = (
    "derive",
    "has_trait",
    "impl",
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
    "Default",
)

from . import derive, has_trait, impl
from .traits.colored import ColoredString, Colorize
from .traits.debug import Debug
from .traits.default import Default
from .traits.functor import Functor, Just, Maybe, Nothing
from .traits.into import From, Into
from .traits.iterator import AdvancedIterator

# combo impls


@impl(Debug >> ColoredString)
@impl(Debug >> Maybe)
class DebugRepr:
    def fmt(self):
        return repr(self)
