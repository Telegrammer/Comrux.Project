import pytest
from uuid import uuid4
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.enums import ProjectRole
from infrastructure.models import Project, User, ProjectMembership
from infrastructure.models.base import Base

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


class TestProjectMembership:
    def test_create_membership(self, session):
        # Create test entities
        user = User(
            id_=uuid4(),
            name="Test User",
            bio="Test Bio",
            birthdate=date(1990, 1, 1)
        )
        project = Project(
            id_=uuid4(),
            title="Test Project",
            description="Test Description",
            created_at=datetime.now()
        )
        
        # Create membership
        membership = ProjectMembership(
            project_id=project.id_,
            user_id=user.id_,
            role=ProjectRole.owner
        )

        session.add_all([user, project, membership])
        session.commit()

        # Verify creation
        saved_membership = session.get(ProjectMembership, (project.id_, user.id_))
        
        assert saved_membership.role == ProjectRole.owner
        assert saved_membership.project == project
        assert saved_membership.user == user

        logger.debug("Project members %s", project.members)

    def test_relationship_back_populates(self, session):
        user = User(id_=uuid4(), name="User")
        project = Project(id_=uuid4(), title="Project", created_at=datetime.now())
        membership = ProjectMembership(
            project_id=project.id_,
            user_id=user.id_,
            role=ProjectRole.member
        )

        session.add_all([user, project, membership])
        session.commit()

        assert membership in project.members
        assert membership in user.memberships

    def test_required_fields(self, session):
        with pytest.raises(Exception):  # Specific exception depends on your DB
            membership = ProjectMembership(
                project_id=uuid4(),
                user_id=uuid4(),
                # Missing role
            )
            session.add(membership)
            session.commit()


class TestProject:
    def test_create_project(self, session):
        project = Project(
            id_=uuid4(),
            title="Test Project",
            description="Test Description",
            created_at=datetime.now()
        )

        session.add(project)
        session.commit()

        saved_project = session.get(Project, project.id_)
        assert saved_project.title == "Test Project"
        assert saved_project.description == "Test Description"
        assert isinstance(saved_project.created_at, datetime)

    def test_optional_description(self, session):
        project = Project(
            id_=uuid4(),
            title="Test Project",
            created_at=datetime.now()
        )

        session.add(project)
        session.commit()

        saved_project = session.get(Project, project.id_)
        assert saved_project.description is None

    def test_project_members_relationship(self, session):
        project = Project(id_=uuid4(), title="Test", created_at=datetime.now())
        user = User(id_=uuid4(), name="Member User")
        membership = ProjectMembership(
            project_id=project.id_,
            user_id=user.id_,
            role=ProjectRole.member
        )

        session.add_all([project, user, membership])
        session.commit()

        assert len(project.members) == 1
        assert project.members[0].user == user


class TestUser:
    def test_create_user(self, session):
        user = User(
            id_=uuid4(),
            name="Test User",
            bio="Test Bio",
            birthdate=date(1990, 1, 1)
        )

        session.add(user)
        session.commit()

        saved_user = session.get(User, user.id_)
        assert saved_user.name == "Test User"
        assert saved_user.bio == "Test Bio"
        assert saved_user.birthdate == date(1990, 1, 1)

    def test_optional_fields(self, session):
        user = User(
            id_=uuid4(),
            name="Test User"
        )

        session.add(user)
        session.commit()

        saved_user = session.get(User, user.id_)
        assert saved_user.bio is None
        assert saved_user.birthdate is None

    def test_user_memberships_relationship(self, session):
        user = User(id_=uuid4(), name="Test User")
        project = Project(id_=uuid4(), title="Test Project", created_at=datetime.now())
        membership = ProjectMembership(
            project_id=project.id_,
            user_id=user.id_,
            role=ProjectRole.owner
        )

        session.add_all([user, project, membership])
        session.commit()

        assert len(user.memberships) == 1
        assert user.memberships[0].project == project


def test_cascade_behavior(session):
    # Test proper cascade deletion if configured in relationships
    project = Project(id_=uuid4(), title="Test", created_at=datetime.now())
    user = User(id_=uuid4(), name="User")
    membership = ProjectMembership(
        project_id=project.id_,
        user_id=user.id_,
        role=ProjectRole.owner
    )

    session.add_all([project, user, membership])
    session.commit()

    # Verify initial state
    assert session.query(ProjectMembership).count() == 1

    # Test deletion behavior (adjust according to your cascade rules)
    session.delete(project)
    session.commit()

    # Check membership was deleted (if cascade="delete" is set)
    assert session.query(ProjectMembership).count() == 0