# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("From", "Into")

from .. import Trait, impl

class From(Trait):
    def __generic__(cls, source: type):
        cls.source = source

        return [source] # TODO: make this neater

    def __reciprocal__(cls, ty):
        impl(Into[ty] >> cls.source)(
            type(f"Auto{cls.source.__name__.title()}Into{ty.__name__.title()}", tuple(), {}))

    def from_(val): ...

class Into(Trait):
    def __generic__(cls, target: type):
        cls.target = target

        return [target]

    @classmethod
    def into(cls, val):
        return From[val.__class__](cls.target).from_(val)



# These are not impl-ed by default


def impl_defaults():
    HEX_CHARS = tuple("abcdef")

    @impl(From[str] >> float)
    class FloatFromStr:
        def from_(self, value) -> float:
            return self(value)

    @impl(From[str] >> int)
    class IntFromStr:
        def from_(self, value) -> int:
            if any(c.lower() in HEX_CHARS for c in value):
                return int(value, 16)

            return int(value, 0)
