from fastapi import APIRouter

router = APIRouter()
@router.get("/health")
async def status():
    return {"status":"ok"}
    