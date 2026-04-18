from domain.entities import Project, ProjectGroup, ProjectGroupId, ProjectId, UserId
from domain.enums import ProjectRole
from domain.exceptions import (
    ProjectGroupAdmissionError,
    ProjectGroupDuplicateParticipantError,
    ProjectGroupOwnerInParticipantsError,
    ProjectGroupParticipantNotInProjectError,
)
from domain.ports import ProjectGroupIdGenerator
from domain.value_objects import Color, HexColor, Title


class ProjectGroupService:
    def __init__(self, id_generator: ProjectGroupIdGenerator) -> None:
        self._id_generator = id_generator

    @staticmethod
    def _ensure_no_duplicates(participants: list[UserId]) -> None:
        if len(participants) != len(set(participants)):
            raise ProjectGroupDuplicateParticipantError(
                "Participants list contains duplicates"
            )

    @staticmethod
    def _project_member_ids(project: Project) -> set[UserId]:
        return set(project.members.keys())

    @staticmethod
    def _ensure_participants_belong_to_project(
        project: Project, participants: list[UserId]
    ) -> None:
        members = ProjectGroupService._project_member_ids(project)
        for participant in participants:
            if participant not in members:
                raise ProjectGroupParticipantNotInProjectError(
                    "Participant does not belong to project"
                )

    @staticmethod
    def _ensure_owner_is_not_in_participants(
        project: Project, participants: list[UserId]
    ) -> None:
        owner_ids = {
            user_id for user_id, role in project.members.items() if role == ProjectRole.OWNER
        }
        if any(participant in owner_ids for participant in participants):
            raise ProjectGroupOwnerInParticipantsError(
                "Project owner cannot be provided in participants list"
            )

    def create_group(
        self,
        name: Title,
        color: Color,
        project: Project,
        owner: UserId,
        participants: list[UserId] | None = None,
        *,
        is_public: bool,
    ) -> ProjectGroup:
        normalized = participants if participants else []
        self._ensure_no_duplicates(normalized)
        self._ensure_owner_is_not_in_participants(project, normalized)
        self._ensure_participants_belong_to_project(project, normalized)

        owner_id = owner
        if owner_id not in self._project_member_ids(project):
            raise ProjectGroupParticipantNotInProjectError(
                "Owner does not belong to project"
            )
        if owner_id not in normalized:
            normalized.append(owner_id)

        return ProjectGroup(
            id_=self._id_generator(),
            project_id=ProjectId(project.id_),
            name=name,
            color=color,
            owner=owner_id,
            participants=normalized,
            is_public=is_public,
        )

    def join(
        self,
        group: ProjectGroup,
        participant_id: UserId,
        actor_id: UserId,
    ) -> ProjectGroup:
        participant = participant_id
        if participant in group.participants:
            return group

        group_owner = UserId(group.owner)
        actor = actor_id

        if actor != participant and actor != group_owner:
            raise ProjectGroupAdmissionError("Only group owner can add another participant")

        if not group.is_public and actor != group_owner:
            raise ProjectGroupAdmissionError(
                "Private group requires admission by group owner"
            )

        return ProjectGroup(
            id_=ProjectGroupId(group.id_),
            project_id=ProjectId(group.project_id),
            name=Title(group.name),
            color=HexColor(group.color),
            owner=group_owner,
            participants=[*group.participants, participant],
            is_public=group.is_public,
        )

    def leave(self, group: ProjectGroup, participant_id: UserId) -> ProjectGroup:
        participant = participant_id
        if participant not in group.participants:
            return group

        return ProjectGroup(
            id_=ProjectGroupId(group.id_),
            project_id=ProjectId(group.project_id),
            name=Title(group.name),
            color=HexColor(group.color),
            owner=UserId(group.owner),
            participants=[user_id for user_id in group.participants if user_id != participant],
            is_public=group.is_public,
        )

    def rename(self, group: ProjectGroup, name: Title) -> ProjectGroup:
        return ProjectGroup(
            id_=ProjectGroupId(group.id_),
            project_id=ProjectId(group.project_id),
            name=name,
            color=HexColor(group.color),
            owner=UserId(group.owner),
            participants=list(group.participants),
            is_public=group.is_public,
        )
