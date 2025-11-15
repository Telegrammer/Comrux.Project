__all__ = [
    "FieldFetcher",
    "SimpleFieldFetcher",
    "FieldFactory",
]


from typing import Protocol


class FieldFetcher[TModel, TField](Protocol):

    def get_field(self, model_object: TModel) -> TField:
        raise NotImplementedError


# TODO make custom error to search parameter mismatch
class SimpleFieldFetcher[TModel, TField]:

    def __init__(self, name: str):
        self._name = name

    def get_field(self, model_object: TModel) -> TField:
        if result := getattr(model_object, self._name, None):
            return result
        raise ValueError(f"Поле с наименованием {self._name} не найдено")


class FieldFactory:

    _registry: dict[str, FieldFetcher]

    @classmethod
    def register[TModel, TField](cls, name: str, fetcher: FieldFetcher[TModel, TField]):
        cls._registry[name] = fetcher

    @classmethod
    def get_fetcher[TModel, TField](cls, name: str) -> FieldFetcher[TModel, TField]:
        if name not in cls._registry:
            return SimpleFieldFetcher[TModel, TField](name)
        return cls._registry[name]
