from .base import DomainError


class ProjectTaskAssignmentForbiddenError(DomainError): ...


class ProjectTaskInvalidStatusTransitionError(DomainError): ...


class ProjectTaskAssigneeContextError(DomainError): ...
