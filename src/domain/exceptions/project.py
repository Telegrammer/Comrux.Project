__all__ = ["ProjectMustHaveOwnerError"]


from .base import DomainError


class ProjectMustHaveOwnerError(DomainError): ...


class MemberNotFoundError(DomainError): ...
