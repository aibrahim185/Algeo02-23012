from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from faker import Faker

fake = Faker()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ambalabu.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

DATA = [
    {
        "id": i,
        "image": "/favicon.ico",
        "title": fake.sentence(nb_words=5),  # Title berupa kalimat acak
    }
    for i in range(1, 102)  
]

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int


@app.get("/faker", response_model=PaginatedResponse)
def get_items(page: int = Query(1, gt=0), size: int = Query(10, gt=0)):
    start = (page - 1) * size
    end = start + size
    items = DATA[start:end]
    total = len(DATA)
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }

@app.get("/")
def hello_world():
    return {"Hello": "World"}

@app.get("/sorong")
def sorong():
    return {"ambalabu": "jangan ke sini~"}
    
@app.get("/music")
def sorong():
    return {"text": "ini api music"}

@app.get("/album")
def sorong():
    return {"text": "ini api album"}
