__all__ = ["OrdersPresenter"]


import json
from application.ports.gateways.query_params import (
    SortingParam,
)
from presentation.exceptions import (
    IncorrectQueryParameterError,
)

class OrdersPresenter:


    def __call__(self, raw_orders: str) -> list[SortingParam]:
        try:
            parsed: list[dict[str, str]] = json.loads(raw_orders)
            normalized = []
            for item in parsed:
                if not isinstance(item, dict) or len(item) != 1:
                    raise IncorrectQueryParameterError("Each order item must be a single-key dict")
                field, direction = next(iter(item.items()))
                direction = direction.upper()
                if direction not in ("ASC", "DESC"):
                    raise IncorrectQueryParameterError("Direction must be ASC or DESC")
                normalized.append(SortingParam(field, direction))
            return normalized
        except:
            raise IncorrectQueryParameterError("Endpoint doesn't provide that kind of structure")
