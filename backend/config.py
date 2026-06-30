import os

# Dossier où ChromaDB stocke les données
CHROMA_DB_PATH = "./chroma_db"

# Dossier où les fichiers uploadés sont sauvegardés
UPLOAD_DIR = "./uploaded_files"

# Modèle LLM
LLM_MODEL = "phi3:mini"

# Modèle embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Nombre de chunks récupérés par recherche
TOP_K = 5

# Crée le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_DIR, exist_ok=True)