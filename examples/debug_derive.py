# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore
from dataclasses import dataclass

from traitor import derive, impl
from traitor.traits.colored import Colorize
from traitor.traits.debug import Debug


@derive(Debug, Colorize)
@dataclass
class CFrame:
    x: int
    y: int
    z: int

    rx: float
    ry: float
    rz: float

    @classmethod
    def origin(cls) -> "CFrame":
        ...

    def add(self, other: "CFrame") -> "CFrame":
        ...

    def translate(self, x: int, y: int, z: int):
        ...

    @staticmethod
    def zero() -> int:
        ...


cframe = CFrame(23, 4, 12, 98.2, 110.2, 0.002)

print(cframe.fmt())
print(cframe.bright_green().on_black())
