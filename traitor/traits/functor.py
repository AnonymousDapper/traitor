# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("Maybe", "Just", "Nothing", "Functor")

from typing import Callable, Generic, Optional, TypeVar

from .. import impl, trait

A = TypeVar("A")
B = TypeVar("B")


class Maybe(Generic[A]):

    inner: Optional[A]

    __created_nothing = False

    def __new__(cls, value: A):
        if value is None:
            if cls.__created_nothing:
                cls.__created_nothing = True
                return Nothing

        return super().__new__(cls)

    def __init__(self, value: A):
        self.inner = value

    @classmethod
    def _create_nothing(cls):
        return cls(None)

    def is_just(self):
        return self.inner is not None

    def is_nothing(self):
        return self.inner is None

    def unwrap(self):
        if self.is_just():
            return self.inner

        raise ValueError(f"unwrap called on Nothing")

    def fmap(self: Maybe[A], fn: Callable[[A], B]) -> Maybe[B]:
        if self.is_just():
            return Just(fn(self.inner))

        return Nothing

    def __contains__(self, value):
        if self.is_nothing():
            return False

        return self.inner == value

    def __repr__(self):
        if self.is_just():
            return f"Just({self.inner!r})"

        return "Nothing"

    def __str__(self):
        if self.is_just():
            return f"Just({self.inner!s})"

        return "Nothing"


Nothing = Maybe._create_nothing()

Just = Maybe


@trait()
class Functor:
    def fmap(self, fn):
        ...


@impl(Functor >> list)
class ListFunctor:
    def fmap(self, fn):
        return [None if x is None else fn(x) for x in self]


@impl(Functor >> tuple)
class ListFunctor:
    def fmap(self, fn):
        return tuple(None if x is None else fn(x) for x in self)
