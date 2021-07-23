# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("Composable",)

from types import FunctionType, BuiltinFunctionType, BuiltinMethodType, MethodType
from .. import impl, trait, named


class ComposedFn:
    def __init__(self, outer, inner):
        self.outer = outer
        self.inner = inner

        self.__name__ = f"{outer.__name__} . {inner.__name__}"

    def __repr__(self):
        return self.__name__

    def __call__(self, *args, **kwargs):
        return self.outer(self.inner(*args, **kwargs))

@trait()
class Composable:
    @named
    def __matmul__(self, other):
        if callable(other):
            return ComposedFn(self, other)

        return NotImplemented


@impl(Composable >> FunctionType)
class ComposableFn: ...

@impl(Composable >> BuiltinFunctionType)
class ComposableBuiltinFn: ...

@impl(Composable >> MethodType)
class ComposableMethod: ...

#@impl(Composable >> BuiltinMethodType)
#class ComposableBuiltinMethod: ...


@impl(Composable >> ComposedFn)
class ComposableComposed: ...