from fastapi import APIRouter, Depends, Request, Response
from user.user_curd import register_user, update_user, delete_user, user_login, get_current_user, verify_user, resend_otp, google_login_start, google_login_callback, decode_token
from config.database import get_session
from schema.schema import User_register, User_update, UserLogin, VerifyEmail, Resend_otp, GoogleLogin
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from models.model import User
from .limiter import limiter

router = APIRouter(prefix="/auth", tags=["USER"])



@router.post("/register")
def create_user(user:User_register, session:Session = Depends(get_session)):
    result = register_user(user, session)
    return result


@router.put("/update")
def user_update(updateUser:User_update, session:Session = Depends(get_session), loginuser:User = Depends(get_current_user)):
    result = update_user(loginuser.id, updateUser,session)
    return result


@router.delete("/delete")
def user_delete(id:int, session:Session = Depends(get_session)):
    return delete_user(id, session)


@router.post("/login")
def login(data:OAuth2PasswordRequestForm = Depends(), session:Session = Depends(get_session)):
    result = UserLogin(email=data.username, password=data.password)
    return user_login(result, session)
    



@router.get("/currentlogin")
def get_me(loginuser:User = Depends(get_current_user)):
    return loginuser


@router.post("/verify_otp")
@limiter.limit("1/minute")
def user_verify(request:Request, user_verf:VerifyEmail, session:Session = Depends(get_session)):
    result = verify_user(user_verf, session)
    return result


@router.post("/resend_otp")
@limiter.limit("1/minute")
def otp_resend(request:Request, re_send_otp:Resend_otp, session:Session = Depends(get_session)):
    result = resend_otp(re_send_otp, session)
    return result


@router.get("/google/login")
async def google_start():
    return await google_login_start()


@router.get("/google/callback")
async def google_callback(code:str, state:str|None, session:Session = Depends(get_session)):
    return await google_login_callback(code, state, session)


