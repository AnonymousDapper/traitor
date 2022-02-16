# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from traitor import derive
from traitor.traits.default import Default


@derive(Default)
class Foo:
    def __init__(self, text: str, num: int, *, nonce: bool = True):
        self.text = text
        self.num = num
        self.nonce = nonce

    def __str__(self):
        return f"<Foo({self.text!r} - {self.num} [{self.nonce}])>"


print(Default(Foo).default())
