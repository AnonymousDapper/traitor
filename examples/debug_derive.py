# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from dataclasses import dataclass

from traitor import derive, impl, trait
from traitor.traits.colored import Colorize
from traitor.traits.debug import Debug


class A:
    ...


@derive(Debug, Colorize)
@dataclass
class CFrame(A):
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

print("Debug:")

print(cframe.fmt())

print("\nColorize:")

print(cframe.bright_green().on_black())
