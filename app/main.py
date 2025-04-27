from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import database
from .model_loader import load_model_and_tokenizer
from .routes import auth_router, generate_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    model, tokenizer = load_model_and_tokenizer()
    app.state.model = model
    app.state.tokenizer = tokenizer
    yield
    await database.disconnect()

app = FastAPI(title="Legal Argument Generator", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(generate_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
     allow_origins=["http://localhost:5173"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"], 
)



