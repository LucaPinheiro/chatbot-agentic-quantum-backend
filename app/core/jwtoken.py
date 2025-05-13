import jwt 
from typing import Union
from datetime import datetime, timedelta, UTC
from app.core.settings import load_settings

settings = load_settings()

class JWToken:
    @staticmethod
    def encode(user_id: Union[str, dict], permission: int, exp_days: int = 1, exp_hours: int = 0, exp_minutes: int = 0,
               jwt_secret: str = settings.jwt_secret) -> str:
        payload = {
            'user_id': user_id,
            'permission': permission,
            'exp': datetime.now(tz=UTC) + timedelta(days=exp_days, hours=exp_hours, minutes=exp_minutes)
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @staticmethod
    def decode(access_token: str, jwt_secret: str = settings.jwt_secret) -> Union[dict, bool]:
        try:
            return jwt.decode(access_token, jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False


    @staticmethod
    def refresh_token(refresh_token: str, jwt_secret: str = settings.jwt_secret, exp_days=1) -> str:
        return JWToken.encode(JWToken.decode(refresh_token, jwt_secret=jwt_secret), exp_days=exp_days,
                              jwt_secret=jwt_secret)