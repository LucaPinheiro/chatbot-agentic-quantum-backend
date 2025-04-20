import bcrypt

from app.core.settings import load_settings


class Encrypt:
    settings = load_settings()

    
    @staticmethod
    def hash_password(password: str) -> str:
        encrypt_key = settings.ENCRYPT_KEY.encode()
        return bcrypt.hashpw(password.encode(), encrypt_key).decode()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())