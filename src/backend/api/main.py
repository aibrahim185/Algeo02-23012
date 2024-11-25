from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ambalabu.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/")
def home_root():
    return {"Hello": "World"}

@app.get("/sorong")
def home_root():
    return {"ambalabu": "jangan ke sini~"}
