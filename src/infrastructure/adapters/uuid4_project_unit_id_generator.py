import uuid


from domain.ports import ProjectUnitIdGenerator
from domain import ProjectUnitId


class Uuid4ProjectUnitIdGenerator(ProjectUnitIdGenerator):

    def __call__(self) -> ProjectUnitIdGenerator:
        return ProjectUnitId(str(uuid.uuid4()))
