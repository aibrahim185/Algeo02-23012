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

cache = []

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
    cache[:] = copy.deepcopy(similar_images)
    
    print(similar_images[:5])
    print(cache[:5])
    
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

    total = len(cache)
    
    start = (page - 1) * size
    end = start + size
    items = [
        {
            "id": idx,
            "title": f"{round(sim * 100, 3)}%",
            "image": f"/api/uploads/images/{image_files[idx]}",
        }
        for idx, dist, sim in cache[start:end]
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )
    
@app.post("/find_similar_midi")
async def find_similar_midi(query_midi: UploadFile):
    """
    Endpoint untuk mencari file MIDI yang mirip dengan file MIDI yang diunggah.
    - query_midi: File MIDI yang diunggah untuk pencarian
    - threshold: Batas minimal kesamaan untuk menyaring hasil pencarian
    """

    query_dir = os.path.join(UPLOAD_DIR, "query")
    os.makedirs(query_dir, exist_ok=True)

    query_midi_path = os.path.join(query_dir, query_midi.filename)
    with open(query_midi_path, "wb") as f:
        content = await query_midi.read()
        f.write(content)

    similar_midi = get_similar_audio(query_midi_path, threshold=0)

    response_items = []
    for midi_file, similarity in similar_midi:
        response_items.append({
            "id": midi_file,
            "title": f"{round(similarity, 2)}%",
            "midi_file": f"/uploads/audio/{midi_file}",
            "image": "/placeholder.ico",
        })

    return {
        "items": response_items[:5],
        "total": len(similar_midi),
        "page": 1,
        "size": len(similar_midi),
    }

@app.post("/upload_audio_and_convert")
async def upload_audio_and_convert(file: UploadFile):
    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    query_dir = os.path.join(UPLOAD_DIR, "query")
    
    # Ensure directories exist
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(query_dir, exist_ok=True)

    # Save the uploaded WAV file
    audio_path = os.path.join(audio_dir, file.filename)
    with open(audio_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Convert WAV to MIDI
    if not file.filename.endswith(".mid"):
        midi_path = audio_to_midi(audio_path)
    else:
        midi_path = audio_path
    
    # Move MIDI file to the query directory
    shutil.move(midi_path, os.path.join(query_dir, "output.mid"))

    return {"message": "Audio converted to MIDI", "midi_file": "/uploads/query/output.mid"}

def audio_to_midi(audio_path: str) -> str:
    y, sr = librosa.load(audio_path, sr=None)
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Track")
    midi.addTempo(track, time, 120)

    for t in range(pitches.shape[1]):
        pitch = pitches[:, t]
        pitch_max = np.argmax(pitch)
        midi_note = librosa.hz_to_midi(librosa.core.pitch_tuning(pitch_max))
        midi.addNote(track, 0, int(midi_note), time, 1, 100)
        time += 1

    midi_path = os.path.join(UPLOAD_DIR, "output.mid")
    with open(midi_path, "wb") as f:
        midi.writeFile(f)

    return midi_path

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