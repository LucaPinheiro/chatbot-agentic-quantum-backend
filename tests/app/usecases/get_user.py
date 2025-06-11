import pytest
from fastapi import HTTPException
from app.usecases.get_user import UseCase, Controller
from app.schemas.get_user import GetUserRequest, GetUserResponse
from app.helpers.exceptions.exceptions import NotFoundException

class DummyUser:
  def __init__(self, user_id, name, email, permission, created_at):
    self.user_id = user_id
    self.name = name
    self.email = email
    self.permission = permission
    self.created_at = created_at

class DummyUserRepo:
  def __init__(self, user=None):
    self._user = user

  def get_user_by_email(self, email):
    if self._user and self._user.email == email:
      return self._user
    return None

  def get_user_by_id(self, user_id):
    if self._user and self._user.user_id == user_id:
      return self._user
    return None

class DummyRepository:
  def __init__(self, user=None):
    self.user_repo = DummyUserRepo(user)

@pytest.fixture
def user():
  return DummyUser(
    user_id="123",
    name="Test User",
    email="test@example.com",
    permission="admin",
    created_at="2024-01-01T00:00:00"
  )

def test_usecase_execute_by_email(monkeypatch, user):
  monkeypatch.setattr("app.usecases.get_user.Repository", lambda user_repo=True: DummyRepository(user))
  use_case = UseCase()
  req = GetUserRequest(email="test@example.com", user_id=None)
  resp = use_case.execute(req)
  assert isinstance(resp, GetUserResponse)
  assert resp.email == user.email

def test_usecase_execute_by_user_id(monkeypatch, user):
  monkeypatch.setattr("app.usecases.get_user.Repository", lambda user_repo=True: DummyRepository(user))
  use_case = UseCase()
  req = GetUserRequest(email=None, user_id="123")
  resp = use_case.execute(req)
  assert resp.user_id == user.user_id

def test_usecase_execute_not_found(monkeypatch):
  monkeypatch.setattr("app.usecases.get_user.Repository", lambda user_repo=True: DummyRepository(None))
  use_case = UseCase()
  req = GetUserRequest(email="notfound@example.com", user_id=None)
  with pytest.raises(NotFoundException):
    use_case.execute(req)

def test_controller_handle_success(monkeypatch, user):
  monkeypatch.setattr("app.usecases.get_user.Repository", lambda user_repo=True: DummyRepository(user))
  use_case = UseCase()
  controller = Controller(use_case)
  req = GetUserRequest(email="test@example.com", user_id=None)
  resp = controller.handle(req)
  assert resp.email == user.email

def test_controller_handle_not_found(monkeypatch):
  monkeypatch.setattr("app.usecases.get_user.Repository", lambda user_repo=True: DummyRepository(None))
  use_case = UseCase()
  controller = Controller(use_case)
  req = GetUserRequest(email="notfound@example.com", user_id=None)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req)
  assert exc.value.status_code == 404

def test_controller_handle_unexpected_exception(monkeypatch):
  class BrokenUseCase:
    def execute(self, schema):
      raise Exception("unexpected error")
  controller = Controller(BrokenUseCase())
  req = GetUserRequest(email="test@example.com", user_id=None)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req)
  assert exc.value.status_code == 500
  assert "unexpected error" in exc.value.detail