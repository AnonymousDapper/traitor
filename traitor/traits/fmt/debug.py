# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

from __future__ import annotations

__all__ = ("Debug",)

from textwrap import indent

from inspect import signature

from ... import impl, trait, TraitObject

@trait()
class Debug:
    def fmt(self) -> str:
        return repr(self)

def check_indent(text):
    if text.find("\n") != text.rfind("\n"):
        return indent(text, "    ").strip()

    return text

def maybe_none(item):
    return "None" if item is None else Debug.into(item).fmt()

@impl(Debug >> str)
class DebugStr: ...


@impl(Debug >> int)
class DebugInt: ...


@impl(Debug >> float)
class DebugFloat: ...

@impl(Debug >> object)
class DebugType: ...


@impl(Debug >> bool)
class DebugBool: ...


@impl(Debug >> list)
class DebugList:
    def fmt(self):
        if len(self) == 0:
            return "[ ]"

        buf = ["["]

        for v in self:
            buf.append(f"    {check_indent(maybe_none(v))},")

        buf.append("]")

        return "\n".join(buf)


@impl(Debug >> dict)
class DebugDict:
    def fmt(self):
        if len(self) == 0:
            return "{ }"

        buf = ["{"]

        for k, v in self.items():
            buf.append(f"    {check_indent(maybe_none(k))}: {check_indent(maybe_none(v))},")

        buf.append("}")

        return "\n".join(buf)

@impl(Debug >> TraitObject)
class DebugTraitObject:
    def fmt(self):
        obj = self.inner

        buf = [f"trait {self.name} ("]

        for name in self.required_methods:
            sig = signature(getattr(obj, name))
            sig = sig.replace(parameters=tuple(sig.parameters.values())[1:])

            buf.append(f"    {name}{sig}")

        for name in self.fallback_methods:
            sig = signature(getattr(obj, name))
            sig = sig.replace(parameters=tuple(sig.parameters.values())[1:])

            buf.append(f"  * {name}{sig}")

        buf.append(")")

        return "\n".join(buf)


# There be dragons here...

# IMPORTANT: this needs to match the manual implementations down below
IMPLEMENTED_TYPES = {type, str, int, float, bool, list, dict, type(None)}

def derive_all():
    def format_wrapper(self):
        return repr(self)

    # WARNING: very sensitive - arbitrary things cause this to break
    for _type in object.__subclasses__():
        if _type not in IMPLEMENTED_TYPES and _type.__module__ not in ("fishhook"):
            if _type.__module__.startswith("traitor"):
                continue

            # print(f"{_type.__name__}: {_type.__module__}")
            impl(Debug >> _type)(
                type(
                    f"Debug{_type.__name__.title()}", (object,), {"fmt": format_wrapper}
                )
            )
