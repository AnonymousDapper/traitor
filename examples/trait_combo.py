# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

# simple demo of the trait system

from traitor import impl
from traitor.traits.colored import ColoredString, Colorize
from traitor.traits.debug import Debug
from traitor.traits.functor import Functor, Just, Maybe
from traitor.traits.iterator import AdvancedIterator


@impl(Debug >> ColoredString)
class DebugColoredString:
    def fmt(self):
        return str(self)


@impl(Debug >> Maybe)
class DebugMaybe:
    def fmt(self):
        return str(self)


def get_color(s):
    return getattr(s, s.strip())


colors = (
    [
        "red",
        None,
        "green",
        None,
        "blue",
        None,
        "yellow",
        None,
        "magenta",
        None,
        "cyan",
        None,
        "white",
    ]
    .map(Maybe)
    .map(lambda m: m.fmap(lambda s: get_color(s)().on_black().bold()))
    .collect()
)

print(colors.fmt())
