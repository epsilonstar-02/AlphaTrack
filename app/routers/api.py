from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/stocks")
def get_stocks():
    return {"stocks": []}
