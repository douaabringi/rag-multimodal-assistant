import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Configurer l'embedding gratuit HuggingFace
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-base")


# Pas de LLM ici — on utilise Mistral dans query_engine
Settings.llm = None


def get_chroma_collection(collection_name: str = "documents"):
    """
    Crée ou récupère une collection ChromaDB
    """
    # ChromaDB stocke les données dans ce dossier
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(collection_name)
    return client, collection


def create_index(chunks: list, metadata: dict = {}) -> VectorStoreIndex:
    client, collection = get_chroma_collection()

    # Vérifie si ce fichier est déjà indexé
    source = metadata.get("source", "inconnu")
    existing = collection.get(where={"source": source})
    
    if existing and len(existing['ids']) > 0:
        print(f" '{source}' déjà indexé — chargement depuis ChromaDB")
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # Sinon indexe normalement
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            text=chunk,
            metadata={
                "chunk_id": i,
                "source": source,
                "type": metadata.get("type", "text")
            }
        )
        documents.append(doc)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    print(f" {len(chunks)} chunks indexés dans ChromaDB")
    return index

def load_index() -> VectorStoreIndex:
    """
    Charge un index déjà existant depuis ChromaDB
    """
    client, collection = get_chroma_collection()

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )

    return index