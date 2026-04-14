from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ProjectReleaseId


class ProjectReleaseIdGenerator(ABC):
    @abstractmethod
    def __call__(self) -> "ProjectReleaseId":
        raise NotImplementedError
