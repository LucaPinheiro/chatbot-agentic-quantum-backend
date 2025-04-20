from enum import Enum


class UserTypeEnum(Enum):
    ADMIN = "Admin"
    PROFESSOR = "Professor"
    STUDENT = "Estudante"


class UserStatusEnum(Enum):
    ACTIVE = "Ativo"
    INACTIVE = "Inativo"



class AccessClassEnum(Enum):
    ACCEPTED = 1
    DENIED = 2