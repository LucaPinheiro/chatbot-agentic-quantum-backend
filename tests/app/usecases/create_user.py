import pytest
import datetime
import uuid
from app.usecases.create_user import UseCase, Controller, create_user
from app.schemas.create_user import CreateUserRequest, CreateUserResponse
from app.domain.entities.user import User
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import DatabaseException, UnauthorizedException, DuplicatedException
from app.schemas.token import TokenUser
from fastapi import HTTPException

class DummyUserRepo:
  def __init__(self):
    self.users = {}

  def get_user_by_email(self, email):
    return self.users.get(email)

  def create_user(self, user):
    self.users[user.email] = user
    return user

class DummyEncrypt:
  @staticmethod
  def hash_password(password):
    return f"hashed-{password}"

@pytest.fixture
def user_repo(monkeypatch):
  repo = DummyUserRepo()
  monkeypatch.setattr("app.infra.repository.Repository.user_repo", repo)
  return repo

@pytest.fixture
def use_case(monkeypatch, user_repo):
  monkeypatch.setattr("app.infra.repository.Repository", lambda user_repo=True: type("Repo", (), {"user_repo": user_repo})())
  monkeypatch.setattr("app.helpers.utils.encrypt.Encrypt.hash_password", DummyEncrypt.hash_password)
  return UseCase()

@pytest.fixture
def controller(use_case):
  return Controller(use_case)

@pytest.fixture
def admin_user():
  return TokenUser(user_id="adminid", name="Admin", email="admin@test.com", permission=PermissionLevelEnum.ADMIN)

@pytest.fixture
def professor_user():
  return TokenUser(user_id="profid", name="Prof", email="prof@test.com", permission=PermissionLevelEnum.PROFESSOR)

def make_request(permission=PermissionLevelEnum.PROFESSOR):
  return CreateUserRequest(
    name="Test User",
    email=f"user{uuid.uuid4().hex}@test.com",
    password="password123",
    permission=permission
  )

def test_execute_creates_user(use_case, user_repo):
  req = make_request()
  resp = use_case.execute(req)
  assert resp.name == req.name
  assert resp.email == req.email
  assert user_repo.get_user_by_email(req.email) is not None

def test_execute_raises_on_duplicate(use_case, user_repo):
  req = make_request()
  user_repo.create_user(User(
    user_id="id1",
    name=req.name,
    email=req.email,
    password="pw",
    created_at=datetime.datetime.now(),
    permission=req.permission
  ))
  with pytest.raises(DuplicatedException):
    use_case.execute(req)

def test_controller_handle_admin_can_create_professor(controller, admin_user):
  req = make_request(permission=PermissionLevelEnum.PROFESSOR)
  resp = controller.handle(req, admin_user)
  assert resp.email == req.email

def test_controller_handle_professor_cannot_create_admin(controller, professor_user):
  req = make_request(permission=PermissionLevelEnum.ADMIN)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req, professor_user)
  assert exc.value.status_code == 401

def test_controller_handle_professor_cannot_create_professor(controller, professor_user):
  req = make_request(permission=PermissionLevelEnum.PROFESSOR)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req, professor_user)
  assert exc.value.status_code == 401

def test_controller_handle_raises_on_duplicate(controller, admin_user, use_case, monkeypatch):
  req = make_request()
  def raise_dup(_):
    raise DuplicatedException("Usuário já existe")
  monkeypatch.setattr(use_case, "execute", raise_dup)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req, admin_user)
  assert exc.value.status_code == 400

def test_controller_handle_raises_on_db_error(controller, admin_user, use_case, monkeypatch):
  req = make_request()
  def raise_db(_):
    raise DatabaseException("DB error")
  monkeypatch.setattr(use_case, "execute", raise_db)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req, admin_user)
  assert exc.value.status_code == 500

def test_controller_handle_raises_on_unexpected(controller, admin_user, use_case, monkeypatch):
  req = make_request()
  def raise_other(_):
    raise Exception("Other error")
  monkeypatch.setattr(use_case, "execute", raise_other)
  with pytest.raises(HTTPException) as exc:
    controller.handle(req, admin_user)
  assert exc.value.status_code == 500