# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from traitor import impl
from traitor.traits.into import From, Into


class Foo:
    def __init__(self, n):
        self.name = n[::-1]

    def __repr__(self):
        return f"<Foo({self.name})>"


@impl(From[Foo] >> str)
class StrFromFoo:
    def from_(value):
        return value.name[::-1]


@impl(From[str] >> Foo)
class FooFromStr:
    def from_(value):
        return Foo(value)


# >>>>>>>>

f = "asd".into()
print(f)

name = From[Foo](str).from_(f)
print(name)
