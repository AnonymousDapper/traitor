# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("Default",)

from .. import Trait, impl, has_trait

import inspect


def parameter_predicate(param: inspect.Parameter):
    return param.name != "self" and (
        # param.annotation != param.empty and
        param.default == param.empty
        and param.kind != param.VAR_POSITIONAL
        and param.kind != param.VAR_KEYWORD
    )


class Default(Trait):
    def default():
        ...

    @staticmethod
    def __derive__(klass):
        signature = inspect.signature(klass.__init__)
        required_params = filter(parameter_predicate, signature.parameters.values())

        args = []
        kwargs = {}

        for param in required_params:
            if param.annotation != param.empty:
                if type(param.annotation) is type:
                    if has_trait(param.annotation, Default):
                        arg_val = Default(param.annotation).default()

                        if param.kind == param.POSITIONAL_ONLY:
                            args.append(arg_val)
                        else:
                            kwargs[param.name] = arg_val

                        continue

                    raise TypeError(f"Default derive requires type {param.annotation} to implement Default")

                raise TypeError(f"Default derive cannot parse ForwardRef annotation: {param.annotation!r}")

            raise TypeError(f"Default derive cannot parse un-annotated parameter: {param.name}")

        bound = signature.bind_partial(*args, **kwargs)

        return impl(Default >> klass)(
            type(f"Default{klass.__name__}Derived", (object,), {"default": lambda: klass(*bound.args, **bound.kwargs)})
        )


@impl(Default >> int)
class DefaultInt:
    def default() -> int:
        return int()


@impl(Default >> float)
class DefaultFloat:
    def default() -> float:
        return float()


@impl(Default >> str)
class DefaultStr:
    def default() -> str:
        return str()


@impl(Default >> list)
class DefaultList:
    def default() -> list:
        return list()


@impl(Default >> tuple)
class DefaultTuple:
    def default() -> tuple:
        return tuple()


@impl(Default >> dict)
class DefaultDict:
    def default() -> dict:
        return dict()


@impl(Default >> set)
class DefaultSet:
    def default() -> set:
        return set()


@impl(Default >> bool)
class DefaultBool:
    def default() -> bool:
        return bool()
