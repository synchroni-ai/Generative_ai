from datetime import timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from motor.core import AgnosticDatabase
from beanie import PydanticObjectId

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, get_ist_now
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = get_ist_now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = get_ist_now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None


async def get_user_by_username(username: str, db: AgnosticDatabase) -> Optional[User]:
    return await User.find_one({"username": username})


async def create_user(username: str, hashed_password: str, db: AgnosticDatabase) -> User:
    user = User(username=username, hashed_password=hashed_password)
    await user.insert()
    return user


async def get_user_from_token(token: str, db: AgnosticDatabase) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return None
        return await get_user_by_username(username, db)
    except JWTError:
        return None


async def update_user_password(username: str, new_hashed_password: str, db: AgnosticDatabase) -> bool:
    user = await get_user_by_username(username, db)
    if user:
        user.hashed_password = new_hashed_password
        await user.save()
        return True
    return False


async def get_user_by_id(user_id: PydanticObjectId, db: AgnosticDatabase) -> Optional[User]:
    return await User.get(user_id)
