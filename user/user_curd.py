from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from models.model import User
from schema.schema import User_register, User_update, UserLogin, VerifyEmail, Resend_otp
from auth.auth import password_hasher, verify_password, decode_token, create_token, get_current_user, generate_otp, get_otp_expiry, generate_reset_token, hash_reset_token
from auth.password_policy import validate_password_policy
from email_verf.email import send_email_verification
from datetime import datetime, timezone, timedelta
import httpx
import os
import secrets
from urllib.parse import urlencode

def register_user(user:User_register, session:Session):
    try:
        exsisting_user = session.exec(select(User).where(User.email == user.email.strip().lower())).first()

        if exsisting_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This user already exsist")
        
        validate_password_policy(user.password, user.email)

        otp = generate_otp()

        hash_password = password_hasher(user.password)
        hash_otp = password_hasher(otp)
        otp_expiry = get_otp_expiry()
        new_user = User(name=user.name, email=user.email, password_hash=hash_password, email_verification_otp_hash=hash_otp, email_verification_otp_expires_at=otp_expiry)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        send_email_verification(receiver_email=user.email, name=user.name, otp=otp)

        return {"message": "Registered Sucessfully", "user": new_user}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


def update_user(id:int, user_update:User_update, session:Session):
    try:
        user = session.get(User,id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
        
        updated_fields = user_update.model_dump(exclude_unset=True)

        for k,v in updated_fields.items():
            setattr(user, k,v)

        session.add(user)
        session.commit()
        session.refresh(user)

        return {"message":"User Updated sucessfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    

def delete_user(id:int, session:Session):
    try:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
        
        session.delete(user)
        session.commit()

        return {"message":"User deleted sucessfully"}


    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    

def user_login(userlogin:UserLogin, session:Session):
    try:
        user = session.exec(select(User).where(User.email == userlogin.email)).first()
        # , User.email_verified == True
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not found")
        if not user.email_verified:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email not verified. Verify email first")
        
        
        verified_password = verify_password(user.password_hash, userlogin.password)
        if not verified_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,detail="Incorect password")
        
        token = create_token(user.email)

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Internal server error")
        
    

def verify_user(verf_user: VerifyEmail, session: Session):
    try:
        MAX_OTP_ATTEMPTS = 3
        OTP_LOCK_MINUTES = 5

        user = session.exec(select(User).where(User.email == verf_user.email)).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No email found")

        if user.email_verified:
            return {
                "message": "Email is already verified"
            }
        

        now = datetime.now(timezone.utc)

        if user.email_verification_locked_until:

            locked_until = user.email_verification_locked_until

            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)

            if now < locked_until:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts. Try again later.")

            user.email_verification_locked_until = None
            user.email_verification_otp_attempts = 0

            session.add(user)
            session.commit()

        if not user.email_verification_otp_hash:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP is invalid or expired")

        expiry_time = user.email_verification_otp_expires_at

        if not expiry_time:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP is invalid or expired")

        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(tzinfo=timezone.utc)

        if now > expiry_time:

            user.email_verification_otp_hash = None
            user.email_verification_otp_expires_at = None
            user.email_verification_otp_attempts = 0

            session.add(user)
            session.commit()

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP expired")

        password_verif = verify_password(user.email_verification_otp_hash, verf_user.otp)

        if not password_verif:

            user.email_verification_otp_attempts += 1

            if user.email_verification_otp_attempts >= MAX_OTP_ATTEMPTS:

                user.email_verification_otp_hash = None
                user.email_verification_otp_expires_at = None

                user.email_verification_locked_until = (now + timedelta(minutes=OTP_LOCK_MINUTES))

                session.add(user)
                session.commit()

                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed OTP attempts. Try again later.")

            session.add(user)
            session.commit()

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")


        user.email_verified = True
        user.email_verification_otp_hash = None
        user.email_verification_otp_expires_at = None
        user.email_verification_otp_attempts = 0
        user.email_verification_locked_until = None

        session.add(user)
        session.commit()

        return {
            "message": "Email verified successfully"
        }
    
    except HTTPException:
        raise

    except Exception:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Internal server error")
    


def resend_otp(user_cred: Resend_otp, session: Session):
    try:
        RESEND_COOLDOWN_SECONDS = 60
        user = session.exec(select(User).where(User.email == user_cred.email)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No email found"
            )

        if user.email_verified:
                return {
                "message": "Email is already verified"
            }
        
        now = datetime.now(timezone.utc)

        if user.email_verification_last_sent_at:

            last_sent = user.email_verification_last_sent_at

            if last_sent.tzinfo is None:
                last_sent = last_sent.replace(tzinfo=timezone.utc)

            elapsed_seconds = (now - last_sent).total_seconds()

            if elapsed_seconds < RESEND_COOLDOWN_SECONDS:

                remaining_seconds = int(
                    RESEND_COOLDOWN_SECONDS - elapsed_seconds
                )

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {remaining_seconds} seconds before requesting a new OTP"
                )


        otp = generate_otp()

        user.email_verification_otp_hash = password_hasher(otp)

        user.email_verification_otp_expires_at = get_otp_expiry()

        user.email_verification_otp_attempts = 0

        user.email_verification_last_sent_at = now

        user.email_verification_locked_until = None


        session.add(user)
        session.commit()
        session.refresh(user)

        send_email_verification(user.email, user.name, otp)

        return {
            "message": "A new OTP has been sent to your email"
        }

    except Exception as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(e))
    


GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_TOKENINFO_URL = os.getenv("GOOGLE_TOKENINFO_URL")



async def google_login_start():

    state = secrets.token_urlsafe(32)

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }

    google_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    return RedirectResponse(url=google_url)





FRONTEND_URL = "http://localhost:3000"


async def google_login_callback(
    code: str,
    state: str | None,
    session: Session,
):
    # ==========================================
    # 1. Check Google authorization code
    # ==========================================

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authorization code missing",
        )

    # ==========================================
    # 2. Exchange authorization code for tokens
    # ==========================================

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

    if response.status_code != 200:
        print("Google token error:", response.text)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to exchange Google authorization code",
        )

    tokens = response.json()

    # ==========================================
    # 3. Get Google ID token
    # ==========================================

    id_token = tokens.get("id_token")

    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google did not return an ID token",
        )

    # ==========================================
    # 4. Verify Google ID token
    # ==========================================

    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_TOKENINFO_URL,
            params={
                "id_token": id_token,
            },
        )

    if response.status_code != 200:
        print("Google verification error:", response.text)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    # ==========================================
    # 5. Get Google user information
    # ==========================================

    user_info = response.json()

    print("Google user:", user_info)

    # ==========================================
    # 6. Verify Google client ID
    # ==========================================

    if user_info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google client",
        )


    if user_info.get("email_verified") not in (True, "true"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email is not verified",
        )

    email = user_info.get("email")
    name = user_info.get("name") or "Google User"

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google",
        )

    # ==========================================
    # 8. Find existing user
    # ==========================================

    statement = select(User).where(User.email == email)

    user = session.exec(statement).first()

    # ==========================================
    # 9. Create user if doesn't exist
    # ==========================================

    if not user:

        if len(name) < 5:
            name = f"{name} User"

        user = User(
            email=email,
            name=name[:50],
            email_verified=True,
            password_hash=None,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

    # ==========================================
    # 10. Verify existing user
    # ==========================================

    elif not user.email_verified:

        user.email_verified = True

        session.add(user)
        session.commit()
        session.refresh(user)

    # ==========================================
    # 11. CREATE YOUR APPLICATION TOKEN
    # ==========================================

    access_token = create_token(user.email)

    print("Google login successful:", user.email)
    print("Access token created:", bool(access_token))

    # ==========================================
    # 12. REDIRECT TO FRONTEND DASHBOARD
    # ==========================================

    # id_token= 32 bit hex code uuid

    response = RedirectResponse(
    url=f"{FRONTEND_URL}/dashboard?jwt={access_token}",
    status_code=status.HTTP_303_SEE_OTHER,)

    # ==========================================
    # 13. SAVE TOKEN IN COOKIE
    # ==========================================
    response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=False,
    samesite="lax",
    max_age=86400,
    path="/",
)

    print("SET-COOKIE:")
    print(response.headers.get("set-cookie"))

    return response




























# def forgot_password(forgotPassword:ForgotPasswordRequest, session:Session):
#     try:
#         user = session.exec(select(User.email == forgotPassword.email)).first()

#         if not user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This email not exsist")
        
#         raw_token = generate_reset_token()

#         hash_token = hash_reset_token(raw_token)

#         user.password_reset_token_hash = hash_token

#         token_exp = datetime.now(timezone.utc) + timedelta(minutes=5)

#         user.password_reset_token_expires_at = token_exp
#         session.add(user)
#         session.commit()




#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={str(e)})
