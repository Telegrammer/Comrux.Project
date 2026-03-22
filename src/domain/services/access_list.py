from domain.ports.id_generators import AccessListIdGenerator
from domain.value_objects import FileName
from domain.exceptions import DomainFieldError, AccessRuleMismatchError
from domain.entities import Project, User, AccessRule, AccessList, UserId, ProjectId


class AccessListService:

    def __init__(self, id_generator: AccessListIdGenerator):
        self._id_generator = id_generator

    def create_access_list(
        self, name: FileName, owner: User, project: Project, rules: list[AccessRule]
    ) -> AccessList:

        targets: set[AccessRule] = set()

        for rule in rules:
            if rule in targets:
                raise AccessRuleMismatchError(
                    "Access list cannot have multiple rule for same target and action"
                )
            targets.add(rule)

        return AccessList(
            id_=self._id_generator(),
            name=name,
            owner=UserId(owner.id_),
            project=ProjectId(project.id_),
            rules=rules,
        )
