__all__ = ["Uuid4ProjectIdGenerator"]


import uuid


from domain.ports import ProjectIdGenerator
from domain import ProjectId


class Uuid4ProjectIdGenerator(ProjectIdGenerator):

    def __call__(self) -> ProjectId:
        return ProjectId(str(uuid.uuid4()))
