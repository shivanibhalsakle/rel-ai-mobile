from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

router=APIRouter()

@router.get("/me")
async def me(current_user: dict= Depends(get_current_user)):
    return{"uid":current_user["uid"]}