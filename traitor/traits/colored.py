# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# this is about as close as I can get to the Rust crate colored while still being Pythonic

# type: ignore

from __future__ import annotations

from typing import Optional

__all__ = ("Colorize", "ColoredString", "Style", "Styles", "Color")

from collections import namedtuple
from enum import Enum
from re import finditer

from .. import impl, trait

TrueColor = namedtuple("TrueColor", "r g b")

StyleFlagData = namedtuple("StyleFlagData", "mask value")


class Styles(Enum):
    """
    VT seqences for styling
    """

    Clear = StyleFlagData(0, "")
    Bold = StyleFlagData(1, "1")
    Dimmed = StyleFlagData(64, "2")
    Italic = StyleFlagData(8, "3")
    Underline = StyleFlagData(2, "4")
    Blink = StyleFlagData(16, "5")
    Reversed = StyleFlagData(4, "7")
    Hidden = StyleFlagData(32, "8")
    Strikethrough = StyleFlagData(128, "7")

    @classmethod
    def from_int(cls, value):
        if value != 0:
            styles = tuple(filter(lambda s: value & s.value.mask, Styles))

            if styles:
                return styles

        return None

    def to_int(self) -> int:
        return self.value.mask

    def to_str(self) -> str:
        return self.value.value


class Style:
    style: int

    def __init__(self, style: Styles):
        self.style = style.to_int()

    def contains(self, style: Styles) -> bool:
        return style in self

    def add(self, other: Styles):
        self += other

    def __contains__(self, item: Styles) -> bool:
        if isinstance(item, Styles):
            val = item.to_int()

            return self.style & val == val

        return NotImplemented

    def __iadd__(self, other: Styles):
        if isinstance(other, Styles):
            self.style |= other.value.mask
            return self

        return NotImplemented

    def __eq__(self, other: Styles) -> bool:
        if isinstance(other, Styles):
            return self.style == other.to_int()

        return NotImplemented

    def __str__(self):
        styles = Styles.from_int(self.style)

        if styles:
            return ";".join(map(Styles.to_str, styles))

        return Styles.Clear.to_str()


class Color(Enum):
    """
    VT sequences for coloring
    """

    Black = 0
    Red = 1
    Green = 2
    Yellow = 3
    Blue = 4
    Magenta = 5
    Cyan = 6
    White = 7

    BrightBlack = 60
    BrightRed = 61
    BrightGreen = 62
    BrightYellow = 63
    BrightBlue = 64
    BrightMagenta = 65
    BrightCyan = 66
    BrightWhite = 67

    TrueColor = TrueColor

    @classmethod
    def true_color(cls, color) -> Color:
        self = cls.TrueColor

        setattr(self, "color", color)

        return self

    def fg(self):
        if self != Color.TrueColor:
            return str(self.value + 30)
        else:
            return f"38;2;{self.color.r};{self.color.g};{self.color.b}"  # type: ignore

    def bg(self):
        if self != Color.TrueColor:
            return str(self.value + 40)
        else:
            return f"48;2;{self.color.r};{self.color.g};{self.color.b}"  # type: ignore


class ColoredString:
    def __init__(
        self,
        text: str,
        *,
        fg_color: Optional[Color] = None,
        bg_color: Optional[Color] = None,
        style: Optional[Styles] = None,
    ):
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.style = style or Style(Styles.Clear)
        self.inner = text

    def is_plain(self) -> bool:
        return self.fg_color is None and self.bg_color is None and self.style == Styles.Clear

    def compute_style(self) -> str:
        if self.is_plain():
            return ""

        buf = ["\x1B["]
        wrote = False

        if self.style != Styles.Clear:
            buf.append(str(self.style))
            wrote = True

        if self.bg_color is not None:
            if wrote:
                buf.append(";")

            buf.append(self.bg_color.bg())
            wrote = True

        if self.fg_color is not None:
            if wrote:
                buf.append(";")

            buf.append(self.fg_color.fg())

        buf.append("m")
        return "".join(buf)

    def escape_inner_resets(self) -> str:
        if self.is_plain():
            return self.inner

        reset = "\x1B\\[0m"
        r_len = 4

        style = self.compute_style()

        matches = tuple(m.start() for m in finditer(reset, self.inner))

        if not matches:
            return self.inner

        tmp = list(self.inner)

        for idx, offset in enumerate(matches):
            offset = offset + r_len + idx * len(style)

            for c in style:
                tmp.insert(offset, c)
                offset += 1

        return "".join(tmp)

    def __repr__(self):
        return repr(self.inner)

    def __format__(self, spec):
        self.inner = self.inner.__format__(spec)
        return str(self)

    def __str__(self):
        if self.is_plain():
            return self.inner

        return f"{self.compute_style()}{self.escape_inner_resets()}\x1B[0m"


@trait()
class Colorize:
    """
    Enables color and style formatting on an object.
    """

    def color(self, color: Color) -> ColoredString:
        ...

    def on_color(self, color: Color) -> ColoredString:
        ...

    def clear(self) -> ColoredString:
        ...

    def bold(self) -> ColoredString:
        ...

    def dimmed(self) -> ColoredString:
        ...

    def italic(self) -> ColoredString:
        ...

    def underline(self) -> ColoredString:
        ...

    def blink(self) -> ColoredString:
        ...

    def reversed(self) -> ColoredString:
        ...

    def hidden(self) -> ColoredString:
        ...

    def strikethrough(self) -> ColoredString:
        ...

    def black(self) -> ColoredString:
        return self.color(Color.Black)

    def red(self) -> ColoredString:
        return self.color(Color.Red)

    def green(self) -> ColoredString:
        return self.color(Color.Green)

    def yellow(self) -> ColoredString:
        return self.color(Color.Yellow)

    def blue(self) -> ColoredString:
        return self.color(Color.Blue)

    def magenta(self) -> ColoredString:
        return self.color(Color.Magenta)

    def cyan(self) -> ColoredString:
        return self.color(Color.Cyan)

    def white(self) -> ColoredString:
        return self.color(Color.White)

    def bright_black(self) -> ColoredString:
        return self.color(Color.BrightBlack)

    def bright_red(self) -> ColoredString:
        return self.color(Color.BrightRed)

    def bright_green(self) -> ColoredString:
        return self.color(Color.BrightGreen)

    def bright_yellow(self) -> ColoredString:
        return self.color(Color.BrightYellow)

    def bright_blue(self) -> ColoredString:
        return self.color(Color.BrightBlue)

    def bright_magenta(self) -> ColoredString:
        return self.color(Color.BrightMagenta)

    def bright_cyan(self) -> ColoredString:
        return self.color(Color.BrightCyan)

    def bright_white(self) -> ColoredString:
        return self.color(Color.BrightWhite)

    def truecolor(self, r: int, b: int, g: int) -> ColoredString:
        return self.color(Color.true_color(TrueColor(r, g, b)))

    def on_black(self) -> ColoredString:
        return self.on_color(Color.Black)

    def on_red(self) -> ColoredString:
        return self.on_color(Color.Red)

    def on_green(self) -> ColoredString:
        return self.on_color(Color.Green)

    def on_yellow(self) -> ColoredString:
        return self.on_color(Color.Yellow)

    def on_blue(self) -> ColoredString:
        return self.on_color(Color.Blue)

    def on_magenta(self) -> ColoredString:
        return self.on_color(Color.Magenta)

    def on_cyan(self) -> ColoredString:
        return self.on_color(Color.Cyan)

    def on_white(self) -> ColoredString:
        return self.on_color(Color.White)

    def on_bright_black(self) -> ColoredString:
        return self.on_color(Color.BrightBlack)

    def on_bright_red(self) -> ColoredString:
        return self.on_color(Color.BrightRed)

    def on_bright_green(self) -> ColoredString:
        return self.on_color(Color.BrightGreen)

    def on_bright_yellow(self) -> ColoredString:
        return self.on_color(Color.BrightYellow)

    def on_bright_blue(self) -> ColoredString:
        return self.on_color(Color.BrightBlue)

    def on_bright_magenta(self) -> ColoredString:
        return self.on_color(Color.BrightMagenta)

    def on_bright_cyan(self) -> ColoredString:
        return self.on_color(Color.BrightCyan)

    def on_bright_white(self) -> ColoredString:
        return self.on_color(Color.BrightWhite)

    def on_truecolor(self, r: int, b: int, g: int) -> ColoredString:
        return self.on_color(Color.true_color(TrueColor(r, g, b)))

    @staticmethod
    def __derive__(klass):
        @impl(Colorize >> klass)
        class ColorizeDerive:
            def color(self, color: Color) -> ColoredString:
                return ColoredString(str(self), fg_color=color)

            def on_color(self, color: Color) -> ColoredString:
                return ColoredString(str(self), bg_color=color)

            def clear(self) -> ColoredString:
                return ColoredString(str(self), style=Styles.Clear)

            def bold(self) -> ColoredString:
                return ColoredString(str(self)).bold()

            def dimmed(self) -> ColoredString:
                return ColoredString(str(self)).dimmed()

            def italic(self) -> ColoredString:
                return ColoredString(str(self)).italic()

            def underline(self) -> ColoredString:
                return ColoredString(str(self)).underline()

            def blink(self) -> ColoredString:
                return ColoredString(str(self)).blink()

            def reversed(self) -> ColoredString:
                return ColoredString(str(self)).reversed()

            def hidden(self) -> ColoredString:
                return ColoredString(str(self)).hidden()

            def strikethrough(self) -> ColoredString:
                return ColoredString(str(self)).strikethrough()


@impl(Colorize >> ColoredString)
class ColorizeColoredString:
    def color(self, color: Color) -> ColoredString:
        self.fg_color = color
        return self

    def on_color(self, color: Color) -> ColoredString:
        self.bg_color = color
        return self

    def clear(self) -> ColoredString:
        return ColoredString(self.inner)

    def bold(self) -> ColoredString:
        self.style += Styles.Bold
        return self

    def dimmed(self) -> ColoredString:
        self.style += Styles.Dimmed
        return self

    def italic(self) -> ColoredString:
        self.style += Styles.Italic
        return self

    def underline(self) -> ColoredString:
        self.style += Styles.Underline
        return self

    def blink(self) -> ColoredString:
        self.styles += Styles.Blink
        return self

    def reversed(self) -> ColoredString:
        self.styles += Styles.Reversed
        return self

    def hidden(self) -> ColoredString:
        self.styles += Styles.Hidden
        return self

    def strikethrough(self) -> ColoredString:
        self.styles += Styles.Strikethrough


@impl(Colorize >> str)
class ColorizeString:
    def color(self, color: Color) -> ColoredString:
        return ColoredString(self, fg_color=color)

    def on_color(self, color: Color) -> ColoredString:
        return ColoredString(self, bg_color=color)

    def clear(self) -> ColoredString:
        return ColoredString(self, style=Styles.Clear)

    def bold(self) -> ColoredString:
        return ColoredString(self).bold()

    def dimmed(self) -> ColoredString:
        return ColoredString(self).dimmed()

    def italic(self) -> ColoredString:
        return ColoredString(self).italic()

    def underline(self) -> ColoredString:
        return ColoredString(self).underline()

    def blink(self) -> ColoredString:
        return ColoredString(self).blink()

    def reversed(self) -> ColoredString:
        return ColoredString(self).reversed()

    def hidden(self) -> ColoredString:
        return ColoredString(self).hidden()

    def strikethrough(self) -> ColoredString:
        return ColoredString(self).strikethrough()
