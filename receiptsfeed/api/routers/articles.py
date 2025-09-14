from fastapi import APIRouter
router = APIRouter()

@router.get("", summary="List articles (stub)")
def list_articles():
    # Wire this to your DB model; this is a placeholder so the API boots cleanly.
    return []
