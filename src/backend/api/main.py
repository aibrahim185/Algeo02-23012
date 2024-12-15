import json
import time
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
import copy
from midiutil import MIDIFile
import librosa
import numpy as np

from api.ImagePCA import ImagePCA
from api.audio import get_similar_audio

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

mapper = {}

@app.post("/upload_mapper")
async def upload_mapper(mapper_file: UploadFile):
    mapper_path = os.path.join(UPLOAD_DIR, mapper_file.filename)

    with open(mapper_path, "wb") as f:
        content = await mapper_file.read()
        f.write(content)
        
    with open(mapper_path, "r") as f:
        data = json.load(f)
        
        for entry in data:
            if "audio_file" in entry and "pic_name" in entry:
                mapper[entry["audio_file"]] = entry["pic_name"]
                mapper[entry["pic_name"]] = entry["audio_file"]
    
    return {"message": "Mapper uploaded"}

@app.get("/get_uploads", response_model=PaginatedResponse)
def get_uploaded_files(
        page: int = Query(1, gt=0), 
        size: int = Query(10, gt=0),
        search: str = Query("")
    ):
    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    image_dir = os.path.join(UPLOAD_DIR, "images")
    
    image_files = [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".jpeg", ".png"))]
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith((".mid"))]
    
    if search:
        filtered_audio = [file for file in audio_files if search.lower() in file.lower()]
        filtered_images = [file for file in image_files if search.lower() in file.lower()]
    else:
        filtered_audio = audio_files
        filtered_images = image_files

    files = []
    
    for idx, audio_file in enumerate(filtered_audio):
        # related_image = mapper[audio_file] if audio_file in mapper else None
        related_image = mapper.get(audio_file, None)
        
        files.append({
            "id": idx,
            "display": audio_file,
            "title": audio_file,
            "image": f"/api/uploads/images/{related_image}" if related_image else "/placeholder.ico",
            "audio": f"/api/uploads/audio/{audio_file}"
        })
    
    for idx, image_file in enumerate(filtered_images):
        # related_audio = mapper[image_file] if image_file in mapper else None
        related_audio = mapper.get(image_file, None)
        
        files.append({
            "id": idx + len(filtered_audio),
            "display": image_file,
            "title": image_file,
            "image": f"/api/uploads/images/{image_file}",
            "audio": f"/api/uploads/audio/{related_audio}" if related_audio else "/midi/Never_Gonna_Give_You_Up.mid"
        })

    start = (page - 1) * size
    end = start + size
    items = files[start:end]
    total = len(filtered_audio) + len(filtered_images)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )

@app.post("/uploaddata")
async def create_upload_file(file_uploads: List[UploadFile]):
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

cache = []  # Unified cache for both image and MIDI results

@app.post("/find_similar_images")
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
    fit_start = time.time()
    pca = ImagePCA()
    pca.fit(prep_images, mean_array)
    fit_end = time.time()

    # Process the query image
    preprocess_start = time.time()
    with Image.open(BytesIO(content)) as img:
        query_img = pca.preprocessQueryImage(img, width, height)
    preprocess_end = time.time()
        
    # Find similar images
    query_start = time.time()
    similar_images = pca.findSimilarImages(query_img, prep_images, len(image_files))
    query_end = time.time()

    # Update cache with image results
    cache[:] = [
        {
            "display": f"{sim * 100:.2f}%",
            "sim": sim, 
            "dist": dist,
            "image": image_files[idx],
            "audio": mapper.get(image_files[idx], None),
        }
        for idx, dist, sim in similar_images
    ]
    
    return {
        "query": f"{(query_end - query_start) * 1000:.2f}",
        "preprocess": f"{(preprocess_end - preprocess_start) * 1000:.2f}",
        "fit": f"{(fit_end - fit_start) * 1000:.2f}",
    }

@app.post("/find_similar_audio")
async def find_similar_audio(query_audio: UploadFile):
    query_dir = os.path.join(UPLOAD_DIR, "query")
    search_directory = os.path.join(os.path.dirname(__file__), "uploads/audio")

    os.makedirs(query_dir, exist_ok=True)

    query_audio_path = os.path.join(query_dir, query_audio.filename)
    with open(query_audio_path, "wb") as f:
        content = await query_audio.read()
        f.write(content)

    time_start = time.time()
    similar_midi = get_similar_audio(query_audio_path, search_directory)
    time_end = time.time()

    # Update cache with MIDI results
    cache[:] = [
        {
            "display": f"{similarity:.2f}%",
            "sim": similarity,
            "audio": midi_file, 
            "image": mapper.get(midi_file, None),
        }
        for midi_file, similarity in similar_midi
    ]

    return {"time": f"{(time_end - time_start) * 1000:.2f} ms"}

@app.get("/get_cache", response_model=PaginatedResponse)
async def get_cache(
        page: int = Query(1, gt=0), 
        size: int = Query(10, gt=0),
        search: str = Query("")
    ):
    
    if search:
        filtered_cache = [
            entry for entry in cache
            if (search.lower() in entry["image"].lower() or search.lower() in entry["audio"].lower())
        ]
    else:
        filtered_cache = cache
    
    start = (page - 1) * size
    end = start + size
    items = [
        {
            "id": idx,
            "display": item["display"],
            "title": item["audio"] if "audio" in item else item["image"],
            "image": f"/api/uploads/images/" + item["image"] if item["image"] != None else None,
            "audio": f"/api/uploads/audio/" + item["audio"] if item["audio"] != None else None,
            "sim": item["sim"],
            "dist": item["dist"] if "dist" in item else None,
        }
        for idx, item in enumerate(filtered_cache[start:end])
    ]
    
    return PaginatedResponse(
        items=items,
        total=len(filtered_cache),
        page=page,
        size=size,
    )

@app.delete("/delete_data")
async def delete_data():
    exclude_files = {".gitkeep", ".gitignore"}
    
    for file in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file)

        if os.path.isfile(file_path) and file not in exclude_files:
            os.remove(file_path)

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            
    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    image_dir = os.path.join(UPLOAD_DIR, "images")
    query_dir = os.path.join(UPLOAD_DIR, "query")
    
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(query_dir, exist_ok=True)

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