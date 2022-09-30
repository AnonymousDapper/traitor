# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("Debug",)

from inspect import getmembers, isclass, isroutine, signature
from textwrap import indent
from types import BuiltinFunctionType, FunctionType, MappingProxyType, MethodType

from .. import Trait, TraitObject, TraitMeta, impl


class Debug(Trait):
    def fmt(self) -> str:
        return repr(self)

    #@staticmethod
    def __derive__(klass):
        bases = tuple(filter(lambda c: c is not object, klass.__bases__))
        msg = f"class {klass.__name__}"

        if len(bases) > 0:
            msg += f"({', '.join(map(lambda c: c.__name__, bases))})"

        def fmt(self):
            buf = [f"{msg}:"]

            data = tuple(
                filter(
                    lambda p: not p[0].startswith("_"),
                    sorted(getmembers(self), key=lambda p: 1 if isroutine(p[1]) else 0),
                )
            )
            max_len = max(len(name) for name, _ in data if not isroutine(_))

            for name, member in data:
                if isinstance(member, (FunctionType, MethodType, BuiltinFunctionType)):
                    buf.append(f"  {Debug(member.__class__).fmt(member)}")

                else:
                    header = f"  {name:{max_len}} = "
                    buf.append(f"{header}{check_indent(maybe_none(member), len(header))}")

            return "\n".join(buf)

        return impl(Debug >> klass)(type(f"Debug{klass.__name__}Derived", (object,), {"fmt": fmt}))


def check_indent(text, n=2):
    if text.find("\n") != text.rfind("\n"):
        return indent(text, " " * n).strip()

    return text


def maybe_none(item):
    return "None" if item is None else Debug(item.__class__).fmt(item)


@impl(Debug >> str)
@impl(Debug >> int)
@impl(Debug >> float)
@impl(Debug >> bool)
class DebugDefault:
    ...


@impl(Debug >> tuple)
class DebugTuple:
    def fmt(self):
        if len(self) == 0:
            return "( )"

        # if len(self) < 5:
        #    return repr(self)

        buf = ["("]

        for v in self:
            buf.append(f"  {check_indent(maybe_none(v))},")

        buf.append(")")

        return "\n".join(buf)


@impl(Debug >> list)
class DebugList:
    def fmt(self):
        if len(self) == 0:
            return "[ ]"

        buf = ["["]

        for v in self:
            buf.append(f"  {check_indent(maybe_none(v))},")

        buf.append("]")

        return "\n".join(buf)


@impl(Debug >> dict)
@impl(Debug >> MappingProxyType)
class DebugDict:
    def fmt(self):
        if len(self) == 0:
            return "{ }"

        buf = ["{"]

        data = tuple(self.items())

        # headers = [check_indent(maybe_none(k)) for k, _ in data]

        # key_len = max(len(line.strip()) for line in headers)
        # print(key_len)
        # print([k for k in headers if len(k) == key_len][0])

        for k, v in data:
            header = f"  {check_indent(maybe_none(k))}"
            header_len = max(len(line) for line in header.splitlines())

            buf.append(f"{header}: {check_indent(maybe_none(v), header_len + 2)},")

        buf.append("}")

        return "\n".join(buf)


@impl(Debug >> FunctionType)
class DebugFunction:
    def fmt(self):
        return f"{self.__name__}{signature(self)}"


@impl(Debug >> MethodType)
class DebugMethod:
    def fmt(self):
        msg = Debug(self.__func__.__class__).fmt(self.__func__)

        if isclass(self.__self__):
            return f"classmethod | {msg}"

        return msg


@impl(Debug >> BuiltinFunctionType)
class DebugBuiltinFn:
    def fmt(self):
        return f"{self.__name__}{self.__text_signature__}"


@impl(Debug >> TraitObject)
class DebugTraitObject:
    def fmt(self):
        obj = self.inner

        buf = [f"trait {self.name} {{"]

        for name in self.required_methods:
            sig = signature(getattr(obj, name))
            #sig = sig.replace(parameters=tuple(sig.parameters.values())[1:])

            buf.append(f"  {name}{sig}")

        for name in self.fallback_methods:
            sig = signature(getattr(obj, name))
            #sig = sig.replace(parameters=tuple(sig.parameters.values())[1:])

            buf.append(f" *{name}{sig}")

        buf.append("}")

        return "\n".join(buf)


@impl(Debug >> TraitMeta)
class DebugTrait:
    def fmt(self):
        buf = [f"trait {self.name} {{"]

        for name in self._required_methods:
            sig = signature(getattr(self, name))
            #sig = sig.replace(parameters=tuple(sig.parameters.values())[1:])

            buf.append(f"  {name}{sig}")

        for name in self._fallback_methods:
            item = getattr(self, name)
            if type(item) == classmethod:
                item = item.__func__

            sig = signature(item)
            #sig = sig.replace(parameters=tuple(sig.parameters.values())[1:])

            buf.append(f" *{name}{sig}")

        buf.append("}")

        return "\n".join(buf)


# All other impls go above this


@impl(Debug >> object)
class DebugObj:
    ...


# There be dragons here...

# IMPORTANT: this needs to match the manual implementations down below
# IMPLEMENTED_TYPES = {type, str, int, float, bool, list, dict, type(None)}


# def derive_all():
#     def format_wrapper(self):
#         return repr(self)

#     # WARNING: very sensitive - arbitrary things cause this to break
#     for _type in object.__subclasses__():
#         if _type not in IMPLEMENTED_TYPES and _type.__module__ not in ("fishhook"):
#             if _type.__module__.startswith("traitor"):
#                 continue

#             # print(f"{_type.__name__}: {_type.__module__}")
#             impl(Debug >> _type)(type(f"Debug{_type.__name__.title()}", (object,), {"fmt": format_wrapper}))
