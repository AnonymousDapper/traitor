# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

from __future__ import annotations

__all__ = ("impl", "trait", "derive")

import operator
import types
from functools import wraps
from inspect import getmembers, isroutine
from typing import Any, Callable, Generic, Optional, TypeVar

from fishhook import hook, unhook
from typing_extensions import ParamSpec

NO_BODY_FUNCTION_CODE = b"d\x00S\x00"

BUILTIN_TYPES = (
    int,
    float,
    str,
    list,
    dict,
    bool,
    types.FunctionType,
    types.LambdaType,
    types.GeneratorType,
    types.CoroutineType,
    types.AsyncGeneratorType,
    types.CodeType,
    types.CellType,  # type: ignore
    types.MethodType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.ModuleType,
    types.GenericAlias,
    types.TracebackType,
    types.FrameType,
    types.GetSetDescriptorType,
    types.MemberDescriptorType,
    types.MappingProxyType,
)

GET_ATTRIBUTE = object.__getattribute__

D = TypeVar("D", bound=type)
T = TypeVar("T", bound=type)
I = TypeVar("I", bound=type)
A = ParamSpec("A")


def derive(*_traits: TraitObject[D]):
    def inner(_type: T) -> T:
        for _trait in _traits:
            if _trait.has_derive:
                _trait.inner.__derive__(_type)  # type: ignore
            else:
                raise TypeError(f"trait {_trait.name} provides no derive functionality")

        return _type

    return inner


class GetAttributeWrapper:
    __slots__ = ("s", "t", "i")

    def __init__(self, s: MethodSentinel, t: type, i: Any):
        self.s = s  # sentinel
        self.t = t  # trait
        self.i = i  # value instance

    def __getattr__(self, name: Any):

        return GET_ATTRIBUTE(self, "s").get_impl_method(GET_ATTRIBUTE(self, "t"), name, GET_ATTRIBUTE(self, "i"))

    def __repr__(self):
        return repr(GET_ATTRIBUTE(self, "i"))


class MethodSentinel(Generic[T]):
    """
    Wrapper object to handle trait method disambiguation
    """

    instances = {}

    __slots__ = ("target", "traits", "providers", "methods")

    def __init__(self, target: T):
        self.target = target
        self.traits: dict[type, type] = {}
        self.providers: dict[str, dict[type, Callable[[T, *Any], Any]]] = {}
        self.methods: set[str] = set()
        self.__class__.instances[target] = self

    def add_impl(self, trait: TraitObject[D], impl):
        assert trait.inner not in self.traits, f"{trait} already implemented: {impl}"

        for name in trait.trait_methods:
            if name in self.providers:
                self.providers[name][trait.inner] = getattr(impl, name)

            else:
                self.providers[name] = {trait.inner: getattr(impl, name)}

        self.traits[trait.inner] = impl

        self.methods = set(self.providers.keys())

    def remove_impl(self, trait: TraitObject[D]):
        del self.traits[trait.inner]

        for name, data in self.providers.items():
            if trait.inner in data:
                del data[trait.inner]

            if data == {}:
                del self.providers[name]

        self.methods = set(self.providers.keys())

    def disambiguate_trait(self, trait: type, value):
        if trait in self.traits:
            return GetAttributeWrapper(self, trait, value)

        raise RuntimeError(f"Trait {trait.__name__} not implemented for {self.target.__name__}")

    def get_impl_method(self, trait: type, name: str, instance: Any) -> Callable[[T, *Any], Any]:
        method = self.providers[name][trait]

        return method.__get__(instance, instance.__class__)

    @classmethod
    def __call__(cls, self: Any, name: str, *args):
        target_class = GET_ATTRIBUTE(self, "__class__")

        if target_class in cls.instances:
            sentinel = cls.instances[target_class]

            try:
                GET_ATTRIBUTE(self, name)
                has_attr = True
            except:
                has_attr = False

            if name in sentinel.methods and not has_attr:
                if len(sentinel.traits) == 1 or len(sentinel.providers[name]) == 1:
                    method = tuple(sentinel.providers[name].values())[0]

                    return method.__get__(self, sentinel.target)

                nl = "\n"
                sep = "\n\t"

                impls = ((n, trait.__name__) for n, trait in enumerate(sentinel.providers[name].keys(), start=1))

                raise RuntimeError(
                    f"Multiple implementations for `{name}` found.\n\n{nl.join(f'#{n} defined in an implementation of {trait} for type `{sentinel.target.__name__}`{sep}Hint: disambiguate the associated method for #{n}: {trait}.into({self!r}).{name}{nl}' for n, trait in impls)}"
                )

        return GET_ATTRIBUTE(self, name)


class TraitObject(Generic[D]):
    """
    Container for a declared trait class.
    """

    __slots__ = (
        "required_methods",
        "fallback_methods",
        "trait_methods",
        "has_derive",
        "name",
        "inner",
    )

    def __init__(self, inner: D, name: str):
        def get_methods(status_check):
            return tuple(
                name
                for name, m in getmembers(inner, isroutine)
                if not name.startswith("__") and status_check(m.__code__.co_code, NO_BODY_FUNCTION_CODE)
            )

        setattr(inner, "__name__", name)

        self.required_methods = get_methods(operator.eq)

        self.fallback_methods = get_methods(operator.ne)

        self.trait_methods = self.required_methods + self.fallback_methods
        self.name = name
        self.has_derive = hasattr(inner, "__derive__")

        self.inner = inner

    def _get_method(self, name: str):
        if name in self.trait_methods:
            return getattr(self.inner, name)

        raise KeyError(name)

    def _aggregate_methods(self, impl: type):
        impl_methods = tuple(name for name, _ in getmembers(impl, isroutine) if not name.startswith("__"))

        optional = set(self.fallback_methods)

        have = set(impl_methods)
        need = set(self.required_methods)

        assert len(need - (have - optional)) == 0  # this shouldnt ever happen, but we'll see

        for method_name in optional - have:
            setattr(impl, method_name, self._get_method(method_name))

    def _check_trait_coverage(self, impl: type):
        impl_methods = tuple(name for name, _ in getmembers(impl, isroutine) if not name.startswith("_"))

        optional = set(self.fallback_methods)

        have = set(impl_methods) - optional
        need = set(self.required_methods)

        if len(need.symmetric_difference(have)) == 0:
            return True

        did_error = False
        declared_not_defined = need - have
        defined_not_declared = have - need

        trait_name = self.name
        impl_name = impl.__name__
        sep = "\n\t"

        msg = f"Trait implementation {impl_name} of {trait_name} is not compatible with trait definition.\n"

        if declared_not_defined:
            msg += f"These methods are required by the definition of {trait_name}:{sep * bool(declared_not_defined)}{sep.join(declared_not_defined)}\n"
            did_error = True

        if defined_not_declared:
            if did_error:
                msg += "\nAdditionally,\n"

            msg += f"These methods are present in the implementation {impl_name}, but not defined in {trait_name}:{sep * bool(defined_not_declared)}{sep.join(defined_not_declared)}\n"

        raise RuntimeError(msg)

    def into(self, value: Any):
        if hasattr(value, "__sentinel"):
            return getattr(value, "__sentinel").disambiguate_trait(self.inner, value)

        raise RuntimeError(f"{self.name} is not implemented for type {value.__class__}")

    def __rshift__(self: TraitObject[D], other: T) -> ImplTarget[D, T]:
        if isinstance(other, type):
            return ImplTarget(self, other)

        return NotImplemented

    def __repr__(self):
        return repr(self.inner)

    def __str__(self):
        return self.name


class ImplTarget(Generic[D, T]):
    """
    Simple container to properly apply types to an impl-er and impl-ee.
    """

    __slots__ = ("trait", "target")

    def __init__(self, trait: TraitObject[D], target: T):
        self.trait = trait
        self.target = target

    def __repr__(self):
        return f"impl {self.trait!r} for {self.target.__name__}"


class TraitImpl(Generic[D, T, I]):
    """
    Container that handles the actual trait implementation.
    """

    __slots__ = ("trait", "target", "impl")

    def __init__(self, trait: ImplTarget[D, T], impl: I):
        self.trait = trait.trait
        self.target = trait.target
        self.impl = impl

        self.trait._check_trait_coverage(impl)

    def apply(self):
        self.trait._aggregate_methods(self.impl)

        if "__sentinel" not in self.target.__dict__.keys():
            sentinel = MethodSentinel(self.target)

            @wraps(self.target.__getattribute__)
            def wrapper(self, name):
                return sentinel(self, name)

            hook(self.target, "__sentinel")(sentinel)

            hook(self.target, "__getattribute__")(wrapper)

        getattr(self.target, "__sentinel").add_impl(self.trait, self.impl)  # type: ignore

    def revert(self):
        if type(getattr(self.target, "__sentinel", None)) == MethodSentinel:
            sentinel = getattr(self.target, "__sentinel")
            sentinel.remove_impl(self.trait)

            if sentinel.traits == {}:

                unhook(self.target, "__sentinel")
                unhook(self.target, "__getattribute__")


# user facing functions are here


def impl(target: ImplTarget[D, T]):
    def inner(cls: I) -> TraitImpl[D, T, I]:
        if type(cls) == TraitImpl:
            obj = TraitImpl(target, cls.impl)  # type: ignore
            obj.apply()

        else:
            obj = TraitImpl(target, cls)
            obj.apply()

        return obj

    return inner


def trait(name: Optional[str] = None):
    def inner(cls: D) -> TraitObject[D]:
        return TraitObject(cls, name or cls.__name__)

    return inner
