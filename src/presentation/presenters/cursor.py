import json
import base64

from presentation.exceptions import IncorrectQueryParameterError
from presentation.models.cursor import NameCursor


class NameCursorPresenter:

    def encode(model: NameCursor) -> str:

        return base64.urlsafe_b64encode(
            json.dumps(model.model_dump(), separators=(",", ":")).encode("utf-8")
        )

    def decode(cursor: str) -> NameCursor:
        try:
            return NameCursor(
                **(
                    json.loads(
                        base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
                    )
                )
            )
        except Exception as e:
            raise IncorrectQueryParameterError(
                "Decoded cursor doesen't match with query structure", e
            )
