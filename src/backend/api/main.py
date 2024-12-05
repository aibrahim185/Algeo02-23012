from fastapi import FastAPI, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import zipfile
import shutil
from typing import List
from faker import Faker # debug

UPLOAD_DIR= os.path.join(os.path.dirname(__file__), "uploads")

fake = Faker()
app = FastAPI()

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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

@app.post("/uploaddata")
async def create_upload_file(file_uploads: list[UploadFile]):
    delete_data()
    for file in file_uploads:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        if file.filename.endswith(".zip"):
            extract_zip(file_path, UPLOAD_DIR)
        
    return {"filenames": [f.filename for f in file_uploads]}

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

def delete_data():
    exclude_files = {".gitkeep", ".gitignore"}
    
    for file in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file)

        # Jika item adalah file, hapus jika tidak ada dalam exclude_files
        if os.path.isfile(file_path) and file not in exclude_files:
            os.remove(file_path)

        # Jika item adalah direktori, hapus isi direktori (rekursif) dan direktori itu sendiri
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Menghapus direktori dan isinya

    return {"message": "Data deleted"}

def extract_zip(zip_file_path, extract_to_dir, file_to_extract=None):
    """
    Mengekstrak file .zip ke direktori tertentu.
    Jika `file_to_extract` diberikan, hanya file tersebut yang akan diekstrak.
    
    Parameters:
    zip_file_path (str): Path ke file .zip
    extract_to_dir (str): Direktori tujuan untuk ekstraksi
    file_to_extract (str, optional): Nama file dalam .zip yang ingin diekstrak. Jika None, semua file akan diekstrak.
    """
    # Memastikan direktori tujuan ada
    if not os.path.exists(extract_to_dir):
        os.makedirs(extract_to_dir)

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            if file_to_extract:
                # Mengekstrak file tertentu jika file_to_extract diberikan
                zip_ref.extract(file_to_extract, extract_to_dir)
                print(f'File {file_to_extract} berhasil diekstrak ke {extract_to_dir}')
            else:
                # Mengekstrak semua file jika tidak ada file_to_extract
                zip_ref.extractall(extract_to_dir)
                print(f'File .zip berhasil diekstrak ke {extract_to_dir}')
    except FileNotFoundError:
        print(f"File {zip_file_path} tidak ditemukan.")
    except zipfile.BadZipFile:
        print(f"File {zip_file_path} bukan file zip yang valid.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")