import os
import sys
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import UPLOAD_DIR
from services.rag_service import (
    process_and_index_file,
    query_documents,
    get_indexed_documents,
    indexed_documents
)

app = FastAPI(
    title="RAG Multimodal API",
    description="Assistant intelligent pour documents PDF, images et UML",
    version="1.0.0"
)

# Permet d'accéder aux fichiers uploadés directement
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


# ─── ROUTE 1 : Upload ───────────────────────────────
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    allowed = ['pdf', 'png', 'jpg', 'jpeg']
    ext = file.filename.lower().split('.')[-1]
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Type non supporté. Acceptés : {allowed}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_and_index_file(file_path, file.filename)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


# ─── ROUTE 2 : Question ─────────────────────────────
@app.post("/query")
async def query(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question vide")

    result = query_documents(request.question)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# ─── ROUTE 3 : Documents ────────────────────────────
@app.get("/documents")
async def documents():
    return {"documents": get_indexed_documents()}


# ─── ROUTE 4 : Supprimer un document ────────────────
@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Supprime un document spécifique de l'index ET de ChromaDB"""
    global indexed_documents

    before = len(indexed_documents)
    indexed_documents[:] = [d for d in indexed_documents if d["filename"] != filename]

    if len(indexed_documents) == before:
        raise HTTPException(status_code=404, detail=f"Document '{filename}' non trouvé")

    # Supprime de ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection("documents")
        collection.delete(where={"source": filename})
        print(f"✅ '{filename}' supprimé de ChromaDB")
    except Exception as e:
        print(f"Erreur suppression ChromaDB: {e}")

    # Supprime le fichier physique
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Supprime le cache
    cache_path = file_path + ".cache.txt"
    if os.path.exists(cache_path):
        os.remove(cache_path)

    return {"message": f"'{filename}' supprimé avec succès"}


# ─── ROUTE 5 : Reset total ──────────────────────────
@app.delete("/reset")
async def reset_documents():
    global indexed_documents
    indexed_documents.clear()

    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        client.delete_collection("documents")
        print("✅ Collection supprimée")
    except Exception as e:
        print(f"Erreur suppression collection: {e}")

    return {"message": "Base réinitialisée ✅"}


# ─── Route de test ──────────────────────────────────
@app.get("/")
async def root():
    return {"message": "RAG Multimodal API fonctionne !"}