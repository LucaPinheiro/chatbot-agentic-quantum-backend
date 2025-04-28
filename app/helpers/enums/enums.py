from enum import Enum
from enum import IntEnum


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
    
    
class PermissionLevelEnum(IntEnum):
    STUDENT = 1 # aluno
    PROFESSOR = 2 # professor
    ADMIN = 3 # admin

