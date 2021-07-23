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

    def __init__(self, value: A):
        if value is None:
            if self.__class__.__created_nothing:
                raise RuntimeError(f"Nothing instance already exists..")

            self.__class__.__created_nothing = True

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

    def __contains__(self, value):
        if self.is_nothing():
            return False

        return self.inner == value

    def __repr__(self):
        if self.is_just():
            return f"Just({self.inner!r})"

        return "Nothing"

Nothing = Maybe._create_nothing()

Just = Maybe


@trait()
class Functor:
    def fmap(self, fn):
        ...

@impl(Functor >> Maybe)
class MaybeFunctor:
    def fmap(self, fn):
        if self.is_just():
            return Just(fn(self.inner))

        return Nothing

@impl(Functor >> list)
class ListFunctor:
    def fmap(self, fn):
        return [None if x is None else fn(x) for x in self]

@impl(Functor >> tuple)
class ListFunctor:
    def fmap(self, fn):
        return tuple(None if x is None else fn(x) for x in self)