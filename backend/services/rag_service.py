import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import UPLOAD_DIR, TOP_K, LLM_MODEL, EMBEDDING_MODEL
from extraction.pdf_loader import extract_text_from_pdf, split_into_chunks
from extraction.image_loader import extract_text_from_image
from extraction.uml_loader import extract_text_from_uml
from indexing.vector_store import create_index, load_index
from rag.query_engine import create_query_engine, ask_question

import chromadb
from llama_index.core import Settings

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Configure les modèles


# Liste des documents indexés (en mémoire)
indexed_documents = []


def get_file_type(filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return 'pdf'
    elif ext in ['png', 'jpg', 'jpeg']:
        return 'image'
    else:
        return 'unknown'


def process_and_index_file(file_path: str, filename: str) -> dict:
    """
    Extrait le texte d'un fichier et l'indexe dans ChromaDB
    """
    file_type = get_file_type(filename)
    chunks = []

    if file_type == 'pdf':
        text = extract_text_from_pdf(file_path)
        chunks = split_into_chunks(text, chunk_size=200)

    elif file_type == 'image':
        # Détecte si c'est un UML ou une image normale
        # Pour simplifier : si "uml" est dans le nom → UML
        text = extract_text_from_uml(file_path)  # LLaVA pour toutes les images
        chunks = [text] if text.strip() else []

    if not chunks:
        return {"success": False, "message": "Aucun texte extrait"}

    # Indexe dans ChromaDB
    create_index(
        chunks=chunks,
        metadata={"source": filename, "type": file_type}
    )

    # Ajoute à la liste des documents
    indexed_documents.append({
        "filename": filename,
        "type": file_type,
        "chunks": len(chunks)
    })

    return {
        "success": True,
        "filename": filename,
        "type": file_type,
        "chunks_count": len(chunks)
    }


def compute_confidence(response, num_sources: int) -> dict:
    """
    Calcule un indicateur de confiance basé sur :
    - le nombre de sources trouvées
    - le score de similarité moyen des nodes récupérés
    """
    if num_sources == 0:
        return {"level": "low", "label": "Faible", "score": 0}

    scores = []
    for node in response.source_nodes:
        if hasattr(node, "score") and node.score is not None:
            scores.append(node.score)

    avg_score = sum(scores) / len(scores) if scores else 0.5

    # Combine score de similarité + nombre de sources
    if avg_score >= 0.75 and num_sources >= 2:
        return {"level": "high", "label": "Élevée", "score": round(avg_score * 100)}
    elif avg_score >= 0.55 or num_sources >= 1:
        return {"level": "medium", "label": "Moyenne", "score": round(avg_score * 100)}
    else:
        return {"level": "low", "label": "Faible", "score": round(avg_score * 100)}


def query_documents(question: str, filename: str = None) -> dict:
    try:
        index = load_index()

        if filename:
            from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
            filters = MetadataFilters(filters=[
                MetadataFilter(key="source", value=filename)
            ])
            query_engine = index.as_query_engine(
                similarity_top_k=TOP_K,
                filters=filters
            )
        else:
            query_engine = create_query_engine(index)

        response = query_engine.query(question)

        sources = []
        for node in response.source_nodes:
            source_name = node.metadata.get("source", "inconnu")
            if source_name not in [s["filename"] for s in sources]:
                sources.append({
                    "filename": source_name,
                    "url": f"http://localhost:8000/files/{source_name}"
                })

        confidence = compute_confidence(response, len(sources))

        return {
            "success": True,
            "question": question,
            "answer": str(response),
            "sources": sources,
            "confidence": confidence
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_indexed_documents() -> list:
    """
    Retourne la liste des documents indexés
    """
    return indexed_documents

def load_indexed_documents_from_chroma():
    """Reconstruit la liste des documents depuis ChromaDB au démarrage"""
    global indexed_documents
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection("documents")
        results = collection.get()

        seen = {}
        for metadata in results.get("metadatas", []):
            source = metadata.get("source", "inconnu")
            file_type = metadata.get("type", "unknown")
            if source not in seen:
                seen[source] = {"filename": source, "type": file_type, "chunks": 0}
            seen[source]["chunks"] += 1

        indexed_documents.clear()
        indexed_documents.extend(seen.values())
        print(f"✅ {len(indexed_documents)} documents rechargés depuis ChromaDB")
    except Exception as e:
        print(f"⚠️ Impossible de recharger les documents: {e}")


# Appelle cette fonction au chargement du module
load_indexed_documents_from_chroma()