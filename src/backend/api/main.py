from fastapi import FastAPI, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import zipfile
import shutil
import numpy as np
from PIL import Image
from typing import List
import time
from io import BytesIO
from api.ImagePCA import ImagePCA

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

app = FastAPI()

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int

@app.get("/uploads", response_model=PaginatedResponse)
def get_uploaded_files(page: int = Query(1, gt=0), size: int = Query(10, gt=0)):
    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    image_dir = os.path.join(UPLOAD_DIR, "images")
    
    image_files = [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".jpeg", ".png"))]
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith((".mid"))]
    
    files = [
        {"id": idx, "title": file, "image": f"/api/uploads/images/{file}"}
        for idx, file in enumerate(image_files + audio_files)
    ]
    
    start = (page - 1) * size
    end = start + size
    items = files[start:end]
    total = len(files)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }

@app.post("/uploaddata")
async def create_upload_file(file_uploads: list[UploadFile]):
    delete_data()
    
    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    image_dir = os.path.join(UPLOAD_DIR, "images")
    
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    
    for file in file_uploads:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        if file.filename.endswith(".zip"):
            extract_zip(file_path, UPLOAD_DIR)
            
        if file.filename.endswith((".png", ".jpg", ".jpeg")):
            shutil.move(file_path, os.path.join(image_dir, file.filename))
        elif file.filename.endswith(".mid"):
            shutil.move(file_path, os.path.join(audio_dir, file.filename))
        
    return {"filenames": [f.filename for f in file_uploads]}

@app.get("/find_similar_images")
async def find_similar_images(query_image: UploadFile, k: int = Query(5, gt=0)):
    # Load uploaded images for PCA
    image_dir = os.path.join(UPLOAD_DIR, "images")
    images = ImagePCA.loadData(image_dir)

    # Preprocess images
    width = 200
    height = 200
    prep_images, mean_array = ImagePCA.preprocessImages(images, width, height)

    # Initialize and fit the PCA model
    pca = ImagePCA()
    pca.fit(prep_images, mean_array)

    # Process the query image
    with Image.open(BytesIO(await query_image.read())) as img:
        query_img = pca.preprocessQueryImage(img, width, height)
        
    # Find similar images
    similar_images = pca.findSimilarImages(query_img, prep_images, k)
    
    response_items = []
    for idx, dist, sim in similar_images:
        img_path = os.path.join(image_dir, f"{idx}.jpg")
        response_items.append({
            "id": idx,
            "image": f"/uploads/images/{os.path.basename(img_path)}",
            "similarity_percentage": sim * 100
        })
    
    return PaginatedResponse(
        items=response_items,
        total=len(similar_images),
        page=1,
        size=k
    )

def delete_data():
    exclude_files = {".gitkeep", ".gitignore"}
    
    for file in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file)

        if os.path.isfile(file_path) and file not in exclude_files:
            os.remove(file_path)

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    return {"message": "Data deleted"}

def extract_zip(zip_file_path, extract_to_dir, file_to_extract=None):
    """
    Mengekstrak file .zip ke direktori tertentu.
    Jika file_to_extract diberikan, hanya file tersebut yang akan diekstrak.
    
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