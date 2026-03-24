from abc import ABC, abstractmethod


from domain.entities.access_list import AccessRuleTargetVisitor, AccessList


class AccessListMapper[Tdto](ABC):

    @abstractmethod
    def to_dto[Tvis: AccessRuleTargetVisitor](
        self, entity: AccessList, visitor: Tvis
    ) -> Tdto:
        raise NotImplementedError

    @abstractmethod
    def to_domain(self, dto: Tdto) -> AccessList:
        raise NotImplementedError
