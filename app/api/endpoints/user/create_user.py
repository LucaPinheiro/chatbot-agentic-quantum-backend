import uuid

from fastapi import APIRouter
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.utils.encrypt import Encrypt
from app.infra.repository import Repository
from app.schemas.create_user import CreateUserRequest, CreateUserResponse

router = APIRouter()

class CreateUserUseCase:
    repository: Repository
    user_repo: IUserRepository
    
    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo

    def execute(self, schema: CreateUserRequest) -> CreateUserResponse:
        new_id = uuid.uuid4().hex
        hashed_pw = Encrypt.hash_password(schema.password)

        user = User(
            id=new_id,
            name=schema.name,
            email=schema.email,
            password=hashed_pw,
        )

        user_created = self.user_repo.create_user(user)

        return CreateUserResponse(
            id=user_created.id,
            name=user_created.name,
            email=user_created.email,
        )


class CreateUserController:
    def __init__(self, use_case: CreateUserUseCase):
        self.use_case = use_case

    def handle(self, request: CreateUserRequest) -> CreateUserResponse:
        return self.use_case.execute(request)


@router.post("/users", response_model=CreateUserResponse, status_code=201)
def create_user(request: CreateUserRequest):
    controller = CreateUserController(CreateUserUseCase())
    return controller.handle(request)

