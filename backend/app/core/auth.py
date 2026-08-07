import firebase_admin
from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth

if not firebase_admin._apps:
    firebase_admin.initialize_app()

async def get_current_user(authorization:str=Header(...))->dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed authorization header")

    token=authorization.removeprefix("Bearer ")

    try:
        decoded_token=firebase_auth.verify_id_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail= "Invalid or expired token") from exc
    return decoded_token