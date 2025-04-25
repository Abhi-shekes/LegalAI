from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    email: str
    password: str
    name: str   

class UserOut(BaseModel):
    id: int
    email: str
    name: str 

class Token(BaseModel):
    access_token: str
    token_type: str

class CaseInput(BaseModel):
    case_id: str
    facts: str
    ipc_sections: List[str]
    max_new_tokens: int = 1024
    temperature: float = 0.6
    top_p: float = 0.9
