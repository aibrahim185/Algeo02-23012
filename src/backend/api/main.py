from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home_root():
    return {"Hello": "World"}

@app.get("/sorong")
def home_root():
    return {"ambalabu": "jangan ke sini~"}
