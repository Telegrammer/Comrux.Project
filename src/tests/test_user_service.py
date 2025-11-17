import pytest
from datetime import date
from unittest.mock import Mock, patch
from dateutil.relativedelta import relativedelta

# Импорты из вашего кода (пути могут отличаться)
from domain.services import UserService
from domain.entities import User, Project
from domain.value_objects import Name, BirthDate, Id
from domain.ports import UserIdGenerator


class TestUserService:

    @pytest.fixture
    def mock_birthdate_policy(self):
        policy = Mock()
        policy.low_border = date(1900, 1, 1)
        policy.age_border = relativedelta(years=18)
        return policy

    @pytest.fixture
    def mock_id_generator(self):
        generator = Mock(spec=UserIdGenerator)
        generator.return_value = Id("user-123")
        return generator

    @pytest.fixture
    def user_service(self, mock_birthdate_policy, mock_id_generator):
        return UserService(mock_birthdate_policy, mock_id_generator)

    @pytest.fixture
    def sample_project(self):
        return Mock(spec=Project)

    def test_create_user_success(self, user_service, sample_project):
        # Arrange
        now = date(2023, 5, 15)
        name = Name("John Doe")
        bio = "Software Developer"
        birthdate = date(1990, 1, 1)
        projects = [sample_project]

        # Act
        user: User = user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        assert user.id_ == "user-123"
        assert user.name == name.value
        assert user.bio == bio
        assert user.projects == projects
        assert user.birthdate == birthdate

        # Проверяем вызовы зависимостей
        user_service._id_generator.assert_called_once()

    def test_create_user_with_minimum_age(self, user_service, sample_project):
        # Arrange
        now = date(2023, 5, 15)
        name = Name("Young User")
        bio = "Test bio"
        # Пользователю ровно 18 лет
        birthdate = date(2005, 5, 15)
        projects = [sample_project]

        # Act
        user = user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        assert user.id_ == "user-123"
        assert user.name == name.value
        assert isinstance(getattr(user, "__object_birthdate", None), BirthDate)

    def test_create_user_with_empty_projects(self, user_service):
        # Arrange
        now = date(2023, 5, 15)
        name = Name("User Without Projects")
        bio = "No projects"
        birthdate = date(1985, 3, 10)
        projects = []

        # Act
        user = user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        assert user.id_ == "user-123"
        assert user.projects == []

    def test_create_user_id_generator_called(self, user_service, sample_project):
        # Arrange
        now = date(2023, 5, 15)
        name = Name("Test User")
        bio = "Test bio"
        birthdate = date(1995, 8, 20)
        projects = [sample_project]

        # Act
        user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        user_service._id_generator.assert_called_once()

    def test_birthdate_policy_used_correctly(
        self, mock_birthdate_policy, mock_id_generator, sample_project
    ):
        # Arrange
        user_service = UserService(mock_birthdate_policy, mock_id_generator)
        now = date(2023, 5, 15)
        name = Name("Test User")
        bio = "Test bio"
        birthdate = date(1990, 1, 1)
        projects = [sample_project]

        # Mock для BirthDate чтобы проверить параметры
        with patch("domain.services.user.BirthDate") as mock_birthdate_class:
            mock_birthdate_instance = Mock()
            mock_birthdate_class.return_value = mock_birthdate_instance

            # Act
            user = user_service.create_user(now, name, bio, birthdate, projects)

            # Assert
            mock_birthdate_class.assert_called_once_with(
                birthdate,
                mock_birthdate_policy.low_border,
                now,
                mock_birthdate_policy.age_border,
            )

    def test_create_user_with_different_id_generator(self, mock_birthdate_policy):
        # Arrange
        custom_id_generator = Mock(return_value=Id("custom-user-id"))
        user_service = UserService(mock_birthdate_policy, custom_id_generator)

        now = date(2023, 5, 15)
        name = Name("Custom ID User")
        bio = "Test bio"
        birthdate = date(1980, 12, 5)
        projects = []

        # Act
        user = user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        assert user.id_ == "custom-user-id"
        custom_id_generator.assert_called_once()


class TestUserServiceEdgeCases:

    @pytest.fixture
    def user_service(self):
        policy = Mock()
        policy.low_border = date(1900, 1, 1)
        policy.age_border = relativedelta(years=18)
        id_generator = Mock(return_value="test-id")
        return UserService(policy, id_generator)

    def test_create_user_with_special_characters_in_bio(self, user_service):
        # Arrange
        now = date(2023, 5, 15)
        name = Name("Special User")
        bio = "Bio with émojis 🚀 and #hashtags"
        birthdate = date(1995, 7, 20)
        projects = []

        # Act
        user = user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        assert user.bio == bio

    def test_create_user_with_long_name(self, user_service):
        # Arrange
        now = date(2023, 5, 15)
        long_name = "A" * 100  # Длинное имя
        name = Name(long_name)
        bio = "Test bio"
        birthdate = date(1992, 3, 15)
        projects = []

        # Act
        user = user_service.create_user(now, name, bio, birthdate, projects)

        # Assert
        assert user.name == long_name

    def test_create_user_on_leap_day(self, user_service):
        # Arrange
        now = date(2023, 2, 28)  # Не високосный год
        name = Name("Leap Day User")
        bio = "Born on leap day"
        birthdate = date(2000, 2, 29)  # Високосный год
        projects = []

        # Act & Assert - проверяем что не возникает исключений
        user = user_service.create_user(now, name, bio, birthdate, projects)
        assert user is not None
