# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

from __future__ import annotations

__all__ = ("Display",)

from ... import impl, trait


@trait()
class Display:
    def fmt(self) -> str:
        ...


@impl(Display >> str)
class DisplayStr:
    def fmt(self):
        return self


@impl(Display >> int)
class DisplayInt:
    def fmt(self):
        return str(self)


@impl(Display >> float)
class DisplayFloat:
    def fmt(self):
        return str(self)


@impl(Display >> bool)
class DisplayBool:
    def fmt(self):
        return str(self)
