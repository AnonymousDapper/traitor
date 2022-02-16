# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

from __future__ import annotations

# __all__ = ("impl", "derive", "Trait", "has_trait")

import operator
import types
from functools import wraps
from inspect import getmembers, isroutine

from fishhook import hook

NO_BODY_FUNCTION_CODE = b"d\x00S\x00"
GET_ATTRIBUTE = type.__getattribute__
OBJ_GET_ATTRIBUTE = object.__getattribute__

GENERIC_CACHE = {}

@type.__call__
class NULL: ...

def HAS_ATTRIBUTE(obj, key):
    try:
        return GET_ATTRIBUTE(obj, key)

    except:
        return NULL

def OBJ_HAS_ATTRIBUTE(obj, key):
    try:
        return OBJ_GET_ATTRIBUTE(obj, key)

    except:
        return NULL


def check_bind_wrapper(method, instance, klass):
    bound = method.__get__(instance, klass)
    if type(method) == types.MethodType:

        @wraps(method)
        def inner(self, *args, **kwargs):
            return bound(self, *args, **kwargs)

        return inner.__get__(instance, klass)

    return bound


class MethodSentinel:
    def __init__(self, target: type):
        self.target = target

        self.traits = {}
        self.providers = {}
        self.methods = set()

    def add_impl(self, trait: TraitObject, impl):
        assert trait.inner not in self.traits, f"existing implementation for {trait} found: {impl}"

        for name in trait.trait_methods:
            method = getattr(impl, name)

            if name in self.providers:
                self.providers[name][trait.inner] = method

            else:
                self.providers[name] = {trait.inner: method}

        self.traits[trait.inner] = impl
        self.methods = set(self.providers.keys())

    def remove_impl(self, trait: TraitObject):
        return NotImplemented

    def has_impl(self, trait: Trait) -> bool:
        return trait in self.traits

    def get_unbound(self, name):
        if name in self.methods:
            if len(self.traits) == 1 or len(self.providers[name]) == 1:
                return tuple(self.providers[name].values())[0]

            nl = "\n"
            s = "\n\t"

            impls = (
                (n, str(trait), self.traits[trait].__name__)
                for n, trait in enumerate(self.providers[name].keys(), start=1)
            )

            raise RuntimeError(
                f"Multiple implementations of `{name}` for type `{self.target.__name__}` found.\n\n{nl.join(f'#{n} defined in an implementation of `{trait}`: `{impl}`{s}Hint: disambiguate the associated method: {trait}.{name}{nl}' for n, trait, impl in impls)}"
            )

    def __call__(self, val, key):
        #assert type(val) is self.target, f"Mismatched types: {type(val)} - {self.target} ({val} [{key}])"

        if (method := OBJ_HAS_ATTRIBUTE(val, key)) is not NULL:
            return method

        if method := self.get_unbound(key):
            return check_bind_wrapper(method, val, self.target)

        raise AttributeError(key)

    def __repr__(self):
        return f"MethodSentinel<{self.target.__name__}>"


# Root sentinel
@type.__call__
class TypeLevelSentinel:

    # prefer builtin-attributes over trait-provided
    def __call__(self, ty, key):
        if (method := HAS_ATTRIBUTE(ty, key)) is not NULL:
            return method

        if (sentinel := HAS_ATTRIBUTE(ty, "__sentinel")) is not NULL:
            if method := sentinel.get_unbound(key):
                return method

        raise AttributeError(key)

class TraitMeta(type):
    def __getitem__(cls, *args):
        if (cls, args) in GENERIC_CACHE:
            return GENERIC_CACHE[(cls, args)]

        if hasattr(cls, "__generic__"):
            new = TraitMeta(cls.__name__, (Trait,), {**cls.__dict__})
            new.__args__ = new.__generic__(new, *args)
            
            # for k, v in new.__dict__.items():
            #     if type(v) == classmethod:
            #         setattr(new, k, v.__func__.__get__(new, TraitMeta))

            GENERIC_CACHE[(cls, args)] = new

            return new
        
        raise TypeError(f"Trait {cls} defines no generic parameters")

    def __rshift__(cls, other):
        if isinstance(other, type):
            if hasattr(cls, "__reciprocal__"):
                cls.__reciprocal__(cls, other)

            return ImplTarget(TraitObject(cls), other)

        return NotImplemented

    def __repr__(cls):
        if not hasattr(cls, "__args__"):
            return cls.__name__

        return f"{cls.name}[{', '.join(ty.__name__ for ty in cls.__args__)}]"

    def __call__(cls, key):
        if type(key) is type:
            if hasattr(key, "__sentinel"):
                if getattr(key, "__sentinel").has_impl(cls):
                    return getattr(key, "__sentinel").traits[cls]

            else:
                raise TypeError(f"{cls} is not implemented for {key.__name__}")

        else:
            raise TypeError("type specification allowed only with types")

class Trait(object, metaclass=TraitMeta):
    name: str
    _required_methods: tuple
    _fallback_methods: tuple
    _trait_methods: tuple
    _has_derive: bool

    def __init_subclass__(cls):
        def check(m):
            if hasattr(m, "__code__"):
                code = m.__code__

            elif hasattr(m, "__func__"):
                code = m.__func__.__code__

            else:
                raise RuntimeError(f"Unknown `{m}`: {dir(m)}")

            return code.co_code

        def get_methods(stat):
            return tuple(
                name
                for name, m in getmembers(cls, isroutine)
                if not name.startswith("__") and stat(check(m), NO_BODY_FUNCTION_CODE)
            )

        cls._required_methods = get_methods(operator.eq)
        cls._fallback_methods = get_methods(operator.ne)

        cls._trait_methods = cls._required_methods + cls._fallback_methods
        cls.name = cls.__name__
        cls._has_derive = hasattr(cls, "__derive__")


# Resolves method discrepancies between a declaration and an implementation
class TraitObject:
    __slots__ = "required_methods", "fallback_methods", "trait_methods", "has_derive", "name", "inner"

    def __init__(self, inner):
        self.required_methods = inner._required_methods
        self.fallback_methods = inner._fallback_methods
        self.trait_methods = inner._trait_methods
        self.has_derive = inner._has_derive
        self.name = inner.name

        self.inner = inner


    def _get_method(self, name: str):
        if name in self.trait_methods:
            return getattr(self.inner, name)

        raise KeyError(name)

    # Copy default impls over to the provided impl
    def _coalesce_methods(self, impl: type):
        impl_methods = tuple(name for name, _ in getmembers(impl, isroutine) if not name.startswith("__"))

        optional = set(self.fallback_methods)
        have = set(impl_methods)
        need = set(self.required_methods)

        assert len(need - (have - optional)) == 0  # assuming we checked before calling this method

        for name in optional - have:
            setattr(impl, name, self._get_method(name))

    # Ensure our implementation matches our definition
    def _check_coverage(self, impl: type):
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

    def __repr__(self):
        return repr(self.inner)

    def __str__(self):
        return str(self.inner)


# Simple container
class ImplTarget:
    __slots__ = "trait", "target"

    def __init__(self, trait, target: type):
        self.trait = trait
        self.target = target

    def __repr__(self):
        return f"<impl of {self.trait!s} for {self.target.__name__}>"


class TraitImpl:
    __slots__ = "trait", "target", "impl"

    def __init__(self, target: ImplTarget, impl):
        self.trait = target.trait
        self.target = target.target
        self.impl = impl

        self.trait._check_coverage(impl)

    def apply(self):
        self.trait._coalesce_methods(self.impl)

        if "__sentinel" not in self.target.__dict__.keys():
            sentinel = MethodSentinel(self.target)

            @wraps(self.target.__getattribute__)
            def wrapper(o, k):
                return sentinel(o, k)

            hook(self.target, "__sentinel")(sentinel)
            hook(self.target, "__getattribute__")(wrapper)

        GET_ATTRIBUTE(self.target, "__sentinel").add_impl(self.trait, self.impl)


# user facing functions


def impl(target: ImplTarget):
    def inner(cls):
        if cls.__class__ == TraitImpl:
            obj = TraitImpl(target, cls.impl)

        else:
            obj = TraitImpl(target, cls)

        obj.apply()

        return obj

    return inner

def derive(*traits: Trait):
    def inner(ty):
        for trait in traits:
            if trait._has_derive: # type: ignore
                trait.__derive__(ty) # type: ignore
            else:
                raise TypeError(f"trait {trait} provides no derive candidate")

        return ty

    return inner

def has_trait(value, trait: TraitObject):
    if hasattr(value, "__sentinel"):
        return value.__sentinel.has_impl(trait)

    return False



# bad things here
@wraps(type.__getattribute__)
def type_wrapper(t, n):
    return TypeLevelSentinel(t, n)


hook(type, "__getattribute__")(type_wrapper)
