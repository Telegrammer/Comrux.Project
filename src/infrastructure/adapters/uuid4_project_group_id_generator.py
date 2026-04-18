import uuid

from domain.entities import ProjectGroupId
from domain.ports import ProjectGroupIdGenerator


class Uuid4ProjectGroupIdGenerator(ProjectGroupIdGenerator):
    def __call__(self) -> ProjectGroupId:
        return ProjectGroupId(str(uuid.uuid4()))
