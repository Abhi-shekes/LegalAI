from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from .database import database
from .schemas import users
from .config import SECRET_KEY, ALGORITHM
from .models import UserOut
from .utils import verify_password
from .schemas import blacklisted_tokens

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_user_by_email(email: str):
    query = users.select().where(users.c.email == email)
    result = await database.fetch_one(query)
    return result if result else None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    try:
        query = blacklisted_tokens.select().where(blacklisted_tokens.c.token == token)
        blacklisted = await database.fetch_one(query)
        if blacklisted:
            raise HTTPException(status_code=401, detail="Token revoked")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserOut(id=user["id"], email=user["email"], name=user["name"])
