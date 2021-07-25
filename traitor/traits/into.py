# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = (
    "From",
    "Into",
)

from typing import Type, TypeVar

from .. import Trait, TraitMeta, impl, trait

T = TypeVar("T", bound=Type)

CLASS_CACHE: dict[str, dict[Type, Type]] = {"Into": {}, "From": {}}

HEX_CHARS = tuple("abcdef")


class FromMeta(TraitMeta):
    __name__: str

    def __getitem__(cls, key):
        if key in CLASS_CACHE["From"]:
            return CLASS_CACHE["From"][key]

        new = FromTMeta(f"From{key.__name__.title()}", (From,), {**cls.__dict__, "__target__": key})

        CLASS_CACHE["From"][key] = new

        return new


class FromTMeta(FromMeta):
    def __repr__(cls):
        return f"From[{cls.__target__.__name__}]"  # type: ignore

    def __getitem__(cls, _):
        return NotImplemented


class IntoMeta(TraitMeta):
    __name__: str

    def __getitem__(cls, key):
        if key in CLASS_CACHE["Into"]:
            return CLASS_CACHE["Into"][key]

        new = IntoTMeta(f"Into{key.__name__.title()}", (Into,), {**cls.__dict__, "__target__": key})

        CLASS_CACHE["Into"][key] = new

        return new


class IntoTMeta(IntoMeta):
    def __repr__(cls):
        return f"Into[{cls.__target__.__name__}]"  # type: ignore

    def __getitem__(cls, _):
        return NotImplemented


class From(Trait, metaclass=FromMeta):
    def from_(self, value) -> T:
        ...

    def __reciprocal__(cls, _type):
        impl(Into[_type] >> cls.__target__)(
            type(f"Auto{cls.__target__.__name__.title()}Into{_type.__name__.title()}", tuple(), {})
        )


class Into(Trait, metaclass=IntoMeta):
    @classmethod
    def into(cls, self, *args) -> T:
        return From[self.__class__].using(cls.__target__).from_(self, *args)


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
