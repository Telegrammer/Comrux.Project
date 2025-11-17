from datetime import datetime

from domain.value_objects import Title, PassedDatetime
from domain.entities import Project, ProjectId
from domain.ports import ProjectIdGenerator


class ProjectService:

    def __init__(self, id_generator: ProjectIdGenerator):
        self._id_generator = id_generator

    def create_project(self, title: Title, description: str, now: datetime):
        return Project(
            id_=self._id_generator(),
            title=title,
            description=description,
            created_at=PassedDatetime(now, now),
        )

    def update_project(
        self, project: Project, title: Title, description: str, now: datetime
    ) -> Project:
        return Project(
            id_=ProjectId(project.id_),
            title=title,
            description=description,
            created_at=PassedDatetime(project.created_at, now),
        )
