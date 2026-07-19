from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.dbconnect import get_db
from models.history import Historys
from models.user import Users
from utils.JWTBearer import JWTBearer

router = APIRouter(prefix="/history")


@router.get("/all")
def get_history(db: Session = Depends(get_db), user: Users = Depends(JWTBearer())):
    """
    Return the logged-in user's past searches, most recent first.
    Previously the frontend already called this URL (see Gallery.jsx),
    but no matching backend route existed - this closes that gap.
    """
    items = (
        db.query(Historys)
        .filter(Historys.user_id == user.id)
        .order_by(desc(Historys.createdAt))
        .all()
    )

    if not items:
        return []

    return [
        {
            "id": item.id,
            "item_name": item.item_name,
            "link": item.link,
            "created_at": str(item.createdAt),
        }
        for item in items
    ]


@router.delete("/{history_id}")
def delete_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    user: Users = Depends(JWTBearer()),
):
    """Let a user delete a single history entry (only their own)."""
    item = (
        db.query(Historys)
        .filter(Historys.id == history_id, Historys.user_id == user.id)
        .first()
    )
    if not item:
        return {"message": "Item not found"}

    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
