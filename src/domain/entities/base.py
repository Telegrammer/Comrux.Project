__all__ = ["Entity"]

from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Any, TypeVar, Union, get_origin, get_args
import types

from ..value_objects import ValueObject, ValueObjectDescriptor, Id
from ..exceptions import DomainFieldError

import types
from typing import get_args, get_origin, Union


def extract_value_object_type(field_type):
    if isinstance(field_type, type) and issubclass(field_type, ValueObject):
        return field_type

    if get_origin(field_type) in (Union, types.UnionType):
        for arg in get_args(field_type):

            if arg is type(None):
                continue
            if isinstance(arg, type) and issubclass(arg, ValueObject):
                return arg

    return None


class ValueObjectDescriptorMeta(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)

        all_annotations = {}
        for base in reversed(new_class.__mro__):
            if hasattr(base, "__annotations__"):
                all_annotations.update(base.__annotations__)

        for field_name, field_type in all_annotations.items():
            if isinstance(field_type, TypeVar) and field_type.__bound__:
                field_type = field_type.__bound__

            vo_type = extract_value_object_type(field_type)

            if vo_type is None:
                continue

            current_attr = getattr(new_class, field_name, None)
            if not isinstance(current_attr, ValueObjectDescriptor):
                setattr(new_class, field_name, ValueObjectDescriptor(field_name))

        return new_class


class EntityMeta(ABCMeta, ValueObjectDescriptorMeta): ...


@dataclass(eq=False)
class Entity[IdT: Id](metaclass=EntityMeta):

    id_: IdT = field(init=True, repr=True, compare=True)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "id_" and getattr(self, "id_", None) is not None:
            raise DomainFieldError("Changing entity ID is not permitted.")
        super().__setattr__(name, value)

    def __eq__(self, other: "Entity") -> bool:
        return other.id_ == self.id_

    def __hash__(self) -> int:
        return hash((type(self), self.id_))


@dataclass
class AggregationRoot[IdT: Id](Entity[IdT]): ...
