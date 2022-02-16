# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("Maybe", "Just", "Nothing", "Functor")


from .. import Trait, impl

class Maybe:
    __nothing = None
    def __new__(cls, value):

        if value is None:
            if not cls.__nothing:
                cls.__nothing = super().__new__(cls)
                cls.__nothing.inner = None

            return cls.__nothing

        self = super().__new__(cls)
        self.inner = value

        return self

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

    def __str__(self):
        if self.is_just():
            return f"Just({self.inner!s})"

        return "Nothing"


@type.__call__
class Nothing(Maybe):
    def __new__(cls):
        return super().__new__(cls, None)

class Just(Maybe):
    def __init__(self, _):
        assert self.is_just()


class Functor(Trait):
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
