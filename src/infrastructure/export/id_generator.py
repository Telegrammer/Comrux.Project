import uuid

from domain.export.models import ProjectReleaseId
from domain.export.ports import ProjectReleaseIdGenerator


class Uuid4ProjectReleaseIdGenerator(ProjectReleaseIdGenerator):
    def __call__(self) -> ProjectReleaseId:
        return ProjectReleaseId(str(uuid.uuid4()))
