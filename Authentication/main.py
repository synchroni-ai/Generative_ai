from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB setup
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]

# Environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY environment variable not set!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    username: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user(username: str):
    return await users_collection.find_one({"username": username})


# Routes
@app.post("/register")
async def register(user: UserRegister):
    if await get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = hash_password(user.password)
    await users_collection.insert_one(
        {"username": user.username, "hashed_password": hashed_pw}
    )
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(user: UserLogin):
    db_user = await get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
async def protected_route(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization[len("Bearer ") :]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")

    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"message": f"Hello, {username}! You are authenticated."}


@app.post("/api/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    user = await get_user(data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_access_token(
        data={"sub": data.username}, expires_delta=timedelta(minutes=15)
    )

    # In a real app, you'd send this via email
    return {
        "reset_token": reset_token,
        "message": "Password reset token generated. Send this to user via email.",
    }


@app.post("/api/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")

    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_hashed_pw = hash_password(data.new_password)
    await users_collection.update_one(
        {"username": username}, {"$set": {"hashed_password": new_hashed_pw}}
    )
    return {"message": "Password has been reset successfully"}
