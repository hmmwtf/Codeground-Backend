from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.domain.auth.crud import auth_crud as crud
from src.app.core.token import decode_token
from jose import JWTError

def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        email = decode_token(access_token)
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=401, detail="User is None")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")