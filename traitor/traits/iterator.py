# The MIT License (MIT)

# Copyright (c) 2021 AnonymousDapper

# type: ignore

from __future__ import annotations

__all__ = ("AdvancedIterator",)

import builtins
import itertools
import operator
import sys
import types
from collections import deque
from functools import reduce

from .. import impl, trait


@trait()
class AdvancedIterator:
    # basics

    def map(self, predicate, *iters):
        return map(predicate, self, *iters)

    def filter(self, predicate):
        return filter(predicate, self)

    def sum(self):
        return sum(self)

    def any(self):
        return any(self)

    def all(self):
        return all(self)

    def zip(self, *iters):
        return zip(self, *iters)

    def len(self):
        return len(self)

    def enumerate(self, start=0):
        return enumerate(self, start=start)

    def reverse(self):
        return reversed(self)

    def reduce(self, collector, default):
        return reduce(collector, self, default)

    def collect(self):
        return list(self)

    # itertools

    def accumulate(self, func=None, *, initial=None):
        return itertools.accumulate(self, func, initial=initial)

    def chain(self, *iters):
        return itertools.chain(self, *iters)

    def combinations(self, r):
        return itertools.combinations(self, r)

    def combinations_with_replacement(self, r):
        return itertools.combinations_with_replacement(self, r)

    def compress(self, selectors):
        return itertools.compress(self, selectors)

    def dropwhile(self, predicate):
        return itertools.dropwhile(predicate, self)

    def filterfalse(self, predicate):
        return itertools.filterfalse(predicate, self)

    def groupby(self, key=None):
        return itertools.groupby(self, key)

    def islice(self, *args):
        return itertools.islice(self, *args)

    def permutations(self, r=None):
        return itertools.permutations(self, r)

    def product(self, *iters, repeat=1):
        return itertools.product(self, *iters, repeat=repeat)

    def starmap(self, func):
        return itertools.starmap(func, self)

    def takewhile(self, predicate):
        return itertools.takewhile(predicate, self)

    def tee(self, n=2):
        return itertools.tee(self, n)

    def zip_longest(self, *iters, fillvalue=None):
        return itertools.zip_longest(self, *iters, fillvalue=fillvalue)

    # 3rd party recipes

    def take(self, n):
        return list(self.islice(n))

    def prepend(self, value):
        return self.chain([value])

    # tabulate, maybe

    def tail(self, n):
        return iter(deque(self, maxlen=n))

    def consume(self, n=None):
        if n is None:
            deque(self, maxlen=0)

        else:
            next(self.islice(n, n), None)

    def nth(self, n, default=None):
        return next(self.islice(n, None), default)

    def all_equal(self):
        g == self.groupby()
        return next(g, True) and not next(g, False)

    def quantify(self, predicate=bool):
        return self.map(predicate).sum()

    def pad_none(self):
        return self.chain(itertools.repeat(None))

    def ncycles(self, n):
        return itertools.chain.from_iterable(itertools.repeat(tuple(self), n))

    def dotproduct(self, other):
        return self.map(operator.mul, other).sum()

    # convolve

    def flatten(self):
        return itertools.chain.from_iterable(self)

    # repeatfunc

    def pairwise(self):
        a, b = self.tee()

        next(b, None)
        return a.zip(b)

    def grouper(self, n, fillvalue=None):
        return itertools.zip_longest(*([iter(self)] * n), fillvalue=fillvalue)

    def roundrobin(self, *iters):
        iterables = (self, *iters)

        num_active = len(iterables)
        nexsts = itertools.cycle(iter(it).__next__ for it in iterables)
        while num_active:
            try:
                for next in nexts:
                    yield next()
            except StopIteration:
                num_active -= 1
                nexts = itertools.cycle(nexts.islice(num_active))

    def partition(self, predicate):
        t1, t2 = self.tee()
        return t1.filterfalse(predicate), t2.filter(predicate)

    def chunks_exact(self, n=2):
        """
        Returns an iterator over groups of n elements.
        If the last group is less than n elements, it will not be returned.
        """

        while chunk := list(self.islice(n)):
            if len(chunk) != n:
                break

            yield chunk

    def chunks(self, n=2):
        """
        Returns an iterator over groups of at most n elements.
        """

        while chunk := list(self.islice(n)):
            yield chunk


@impl(AdvancedIterator >> list)
class AIList:
    ...


@impl(AdvancedIterator >> str)
class AIStr:
    ...


@impl(AdvancedIterator >> map)
class AIMap:
    ...


@impl(AdvancedIterator >> filter)
class AIFilter:
    ...


@impl(AdvancedIterator >> enumerate)
class AIEnumerate:
    ...


@impl(AdvancedIterator >> reversed)
class AIReversed:
    ...


@impl(AdvancedIterator >> tuple)
class AITuple:
    ...


@impl(AdvancedIterator >> builtins.range)
class AIRange:
    ...


@impl(AdvancedIterator >> (x for x in "").__class__)
class AIGenerator:
    ...


@impl(AdvancedIterator >> iter([1]).__class__)
class AIListIter:
    ...


@impl(AdvancedIterator >> iter("a").__class__)
class AIStrIter:
    ...


@impl(AdvancedIterator >> iter(range(0)).__class__)
class AIRangeIter:
    ...


@impl(AdvancedIterator >> builtins.zip)
class AIZip:
    ...


@impl(AdvancedIterator >> itertools.accumulate)
class AIAccumulate:
    ...


@impl(AdvancedIterator >> itertools.chain)
class AIChain:
    ...


@impl(AdvancedIterator >> itertools.combinations)
class AICombinations:
    ...


@impl(AdvancedIterator >> itertools.compress)
class AICompress:
    ...


@impl(AdvancedIterator >> itertools.dropwhile)
class AIDropWhile:
    ...


@impl(AdvancedIterator >> itertools.filterfalse)
class AIFilterFalse:
    ...


@impl(AdvancedIterator >> itertools.groupby)
class AIGroupBy:
    ...


@impl(AdvancedIterator >> itertools.islice)
class AIIslice:
    ...


@impl(AdvancedIterator >> itertools.permutations)
class AIPermutations:
    ...


@impl(AdvancedIterator >> itertools.product)
class AIProduct:
    ...


@impl(AdvancedIterator >> itertools.starmap)
class AIStarmap:
    ...


@impl(AdvancedIterator >> itertools.takewhile)
class AITakeWhile:
    ...


@impl(AdvancedIterator >> itertools._tee)
class AITee:
    ...


@impl(AdvancedIterator >> itertools.zip_longest)
class AIZipLongest:
    ...


@impl(AdvancedIterator >> itertools.count)
class AICount:
    ...


@impl(AdvancedIterator >> itertools.cycle)
class AICycle:
    ...


@impl(AdvancedIterator >> itertools.repeat)
class AIRepeat:
    ...
