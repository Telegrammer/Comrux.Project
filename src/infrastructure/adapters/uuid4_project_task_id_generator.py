import uuid

from domain.entities import ProjectTaskId
from domain.ports import ProjectTaskIdGenerator


class Uuid4ProjectTaskIdGenerator(ProjectTaskIdGenerator):
    def __call__(self) -> ProjectTaskId:
        return ProjectTaskId(str(uuid.uuid4()))
