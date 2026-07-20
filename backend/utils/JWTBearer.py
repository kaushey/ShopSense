from fastapi import HTTPException
from fastapi.security import HTTPBearer
from starlette.requests import Request
from models.user import Users
from database.config import JWT_SECRET
from database.dbconnect import SessionLocal
import jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)

        if credentials is None:
            raise HTTPException(status_code=403, detail="No credentials")

        try:
            data = jwt.decode(
                credentials.credentials,
                JWT_SECRET,
                algorithms=["HS256"],
            )

            db = SessionLocal()
            try:
                user = db.query(Users).filter(Users.id == data["id"]).first()
            finally:
                db.close()

            if user is None:
                raise HTTPException(status_code=403, detail="User not found")

            return user

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token expired, please log in again")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=403, detail=f"Invalid token: {e}")
