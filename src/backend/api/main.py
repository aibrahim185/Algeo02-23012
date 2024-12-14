from fastapi import FastAPI, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import zipfile
import shutil
from PIL import Image
from typing import List
from io import BytesIO
from api.ImagePCA import ImagePCA
import copy

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
        {
            "id": idx, 
            "title": file, 
            "image": f"/api/uploads/images/{file}" if file in image_files else "/placeholder.ico",    
        }
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
async def create_upload_file(file_uploads: List[UploadFile]):
    delete_data()

    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    image_dir = os.path.join(UPLOAD_DIR, "images")
    query_dir = os.path.join(UPLOAD_DIR, "query")
    
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(query_dir, exist_ok=True)

    filenames = []

    # Process each uploaded file
    for file in file_uploads:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        filenames.append(file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # If the file is a zip, extract it
        if file.filename.endswith(".zip"):
            extract_zip(file_path, UPLOAD_DIR)

            # After extraction, process extracted files
            for root, dirs, files in os.walk(UPLOAD_DIR):
                for extracted_file in files:
                    extracted_file_path = os.path.join(root, extracted_file)

                    if extracted_file.endswith((".png", ".jpg", ".jpeg")):
                        shutil.move(extracted_file_path, os.path.join(image_dir, extracted_file))
                    elif extracted_file.endswith(".mid"):
                        shutil.move(extracted_file_path, os.path.join(audio_dir, extracted_file))

            os.remove(file_path)

        elif file.filename.endswith((".png", ".jpg", ".jpeg")):
            shutil.move(file_path, os.path.join(image_dir, file.filename))
        
        elif file.filename.endswith(".mid"):
            shutil.move(file_path, os.path.join(audio_dir, file.filename))

    return {"filenames": filenames}

similar_images_cache = []

@app.post("/find_similar_images", response_model=PaginatedResponse)
async def find_similar_images(query_image: UploadFile, k: int = Query(10, gt=0)):
    query_dir = os.path.join(UPLOAD_DIR, "query")
    
    # Clear the contents of the query directory
    for file in os.listdir(query_dir):
        file_path = os.path.join(query_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Save the uploaded query image
    query_image_path = os.path.join(query_dir, query_image.filename)
    content = await query_image.read()
    with open(query_image_path, "wb") as f:
        f.write(content)
    
    # Load uploaded images for PCA
    image_dir = os.path.join(UPLOAD_DIR, "images")
    images = ImagePCA.loadData(image_dir)

    image_files = [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".jpeg", ".png"))]

    # Preprocess images
    width = 200
    height = 200
    prep_images, mean_array = ImagePCA.preprocessImages(images, width, height)

    # Initialize and fit the PCA model
    pca = ImagePCA()
    pca.fit(prep_images, mean_array)

    # Process the query image
    with Image.open(BytesIO(content)) as img:
        query_img = pca.preprocessQueryImage(img, width, height)
        
    # Find similar images
    similar_images = pca.findSimilarImages(query_img, prep_images, len(image_files))
    similar_images_cache[:] = copy.deepcopy(similar_images)
    
    print(similar_images[:5])
    print(similar_images_cache[:5])
    
    response_items = []
    for idx, dist, sim in similar_images:
        response_items.append({
            "id": idx,
            "title": sim * 100,
            "image": f"/api/uploads/images/{image_files[idx]}",
        })
    
    return PaginatedResponse(
        items=response_items,
        total=len(similar_images),
        page=1,
        size=k,
    )
    
@app.get("/get_similar_images", response_model=PaginatedResponse)
async def get_similar_images(page: int = Query(1, gt=0), size: int = Query(10, gt=0)):
    image_dir = os.path.join(UPLOAD_DIR, "images")

    image_files = [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".jpeg", ".png"))]

    total = len(similar_images_cache)
    
    start = (page - 1) * size
    end = start + size
    items = [
        {
            "id": idx,
            "title": f"{round(sim * 100, 3)}%",
            "image": f"/api/uploads/images/{image_files[idx]}",
        }
        for idx, dist, sim in similar_images_cache[start:end]
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
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