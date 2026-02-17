from typing import TypedDict
from domain.entities.document import ContentId


class DirectoryAttributes(TypedDict): ...


class DocumentAttributes(TypedDict):
    content_ref: ContentId
