# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# simple demo of the trait system

# type: ignore

from traitor import impl
from traitor.traits.colored import ColoredString, Colorize
from traitor.traits.fmt.debug import Debug
from traitor.traits.iterator import AdvancedIterator


@impl(Debug >> ColoredString)
class DebugColoredString:
    def fmt(self):
        return str(self)


colors = (
    [" red ", " green ", " blue ", " yellow ", " magenta ", " cyan ", " white "]
    .map(lambda s: getattr(s, s.strip())().on_black())
    .collect()
)

print()
print(colors.fmt())
print()
