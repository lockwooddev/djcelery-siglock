import pytest
from mock import Mock


@pytest.fixture
def add_mock(monkeypatch):
    """ Mock cache add to return Mock object """
    _mock = Mock()
    monkeypatch.setattr('django.core.cache.cache.add', _mock)
    return _mock
