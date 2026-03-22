import uuid


from domain.ports import ContentIdGenerator
from domain.entities.access_list import AccessListId


class Uuid4AccessListIdGenerator(ContentIdGenerator):

    def __call__(self) -> AccessListId:
        return AccessListId(str(uuid.uuid4()))
