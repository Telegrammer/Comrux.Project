import pytest
from dateutil.relativedelta import relativedelta
from datetime import date
from unittest.mock import Mock


@pytest.fixture
def sample_project():
    project = Mock()
    project.name = "Test Project"
    project.description = "Test Description"
    return project


@pytest.fixture
def mock_birthdate_policy():
    policy = Mock()
    policy.low_border = date(1900, 1, 1)
    policy.age_border = relativedelta(years=18)
    return policy


@pytest.fixture
def mock_id_generator():
    generator = Mock()
    generator.return_value = "test-user-id"
    return generator
