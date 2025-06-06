# app/api/routes/auth.py
 
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from motor.core import AgnosticDatabase
 
from app.services import auth_service
from app.db.mongodb import get_db
from app.models import User
from app.api import deps
 
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
 
class RefreshTokenRequest(BaseModel):
    refresh_token: str
 
class LogoutRequest(BaseModel):
    refresh_token: str
 
router = APIRouter()
 
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db=Depends(get_db)):
    if await auth_service.get_user_by_username(user.username, db):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = auth_service.hash_password(user.password)
    await auth_service.create_user(user.username, hashed_pw, db)
    return {"message": "User registered successfully"}
 
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    db_user = await auth_service.get_user_by_username(form_data.username, db)
    if not db_user or not auth_service.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
 
    access_token = auth_service.create_access_token(data={"sub": form_data.username})
    refresh_token = auth_service.create_refresh_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
 
@router.post("/refresh-token")
async def refresh_token(token_data: RefreshTokenRequest, db=Depends(get_db)):
    if await auth_service.is_token_blacklisted(token_data.refresh_token, db):
        raise HTTPException(status_code=401, detail="Token has been revoked.")
 
    username = await auth_service.verify_token(token_data.refresh_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
 
    new_access_token = auth_service.create_access_token(data={"sub": username})
    return {"access_token": new_access_token, "token_type": "bearer"}
 
@router.post("/logout")
async def logout(data: LogoutRequest, db=Depends(get_db)):
    success = await auth_service.blacklist_token(data.refresh_token, db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to blacklist token.")
    return {"message": "Successfully logged out."}
 
@router.get("/protected")
async def protected_route(current_user: User = Depends(deps.get_current_user), db=Depends(get_db)):
    return {
        "message": f"Hello {current_user.username}! Your user ID is {current_user.id}. You are authenticated."
    }
 
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db=Depends(get_db)):
    user = await auth_service.get_user_by_username(data.username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
 
    reset_token = auth_service.create_access_token(data={"sub": data.username}, expires_delta=timedelta(minutes=15))
    return {
        "reset_token": reset_token,
        "message": "Password reset token generated. (Would be emailed in a real app)"
    }
 
@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db=Depends(get_db)):
    user = await auth_service.get_user_from_token(data.token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
 
    new_hashed_pw = auth_service.hash_password(data.new_password)
    success = await auth_service.update_user_password(user.username, new_hashed_pw, db)
 
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update password in DB")
 
    return {"message": "Password has been reset successfully"}
 
 