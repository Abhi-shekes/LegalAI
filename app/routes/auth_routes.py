from fastapi import APIRouter, Depends, Form, HTTPException
from ..auth import get_user_by_email
from ..models import UserCreate, UserOut, Token
from ..utils import create_access_token, hash_password, verify_password
from ..database import database
from ..schemas import users
from datetime import datetime
from jose import JWTError, jwt
from ..config import SECRET_KEY, ALGORITHM
from ..schemas import blacklisted_tokens
from ..auth import oauth2_scheme  

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate):
    db_user = await get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    query = users.insert().values(email=user.email, hashed_password=hashed_pw, name=user.name)  # Add name
    user_id = await database.execute(query)
    return UserOut(id=user_id, email=user.email, name=user.name) 


@router.post("/login", response_model=Token)
async def login(email: str = Form(...), password: str = Form(...)):
    user = await get_user_by_email(email)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token(data={"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}



@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=400, detail="Token has no expiration time")
        
        expires_at = datetime.utcfromtimestamp(exp)
        
        query = blacklisted_tokens.insert().values(
            token=token,
            expires_at=expires_at
        )
        await database.execute(query)
        
        return {"message": "Successfully logged out"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
