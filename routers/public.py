from fastapi import APIRouter

router_public = APIRouter()


@router_public.get("/api/v1/public/")
def register():
    return {"success": "True"}
