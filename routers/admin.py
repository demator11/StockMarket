from fastapi import APIRouter

router_admin = APIRouter()


@router_admin.get("/api/v1/admin/")
def admin():
    return {"success": "True"}
