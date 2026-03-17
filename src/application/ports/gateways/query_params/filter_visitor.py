from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod


if TYPE_CHECKING:
    from .common import EqFilter, InFilter, LikeFilter, RangeFilter, OrFilter


class FilterVisitor[T]:
    @abstractmethod
    def visit_eq(self, param: EqFilter) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_in(self, param: InFilter) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_range(self, param: RangeFilter) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_like(self, param: LikeFilter) -> T:
        raise NotImplementedError
    
    @abstractmethod
    def visit_or(self, param: OrFilter) -> T:
        raise NotImplementedError
