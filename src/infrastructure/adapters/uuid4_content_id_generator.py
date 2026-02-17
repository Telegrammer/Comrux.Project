import uuid


from domain.ports import ContentIdGenerator
from domain.entities.document import ContentId


class Uuid4ContentIdGenerator(ContentIdGenerator):

    def __call__(self) -> ContentId:
        return ContentId(str(uuid.uuid4()))
