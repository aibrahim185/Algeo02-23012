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
