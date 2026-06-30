import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extraction.pdf_loader import extract_text_from_pdf, split_into_chunks
from extraction.image_loader import extract_text_from_image
from extraction.uml_loader import extract_text_from_uml
from indexing.vector_store import create_index
from rag.query_engine import create_query_engine, ask_question

print("=" * 50)
print("PIPELINE RAG MULTIMODAL COMPLET")
print("=" * 50)

all_chunks = []

# ─── PDF ────────────────────────────────────────────
print("\n📄 Extraction PDF...")
pdf_path = "backend/test.pdf"
if os.path.exists(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(text, chunk_size=200)
    all_chunks.extend(chunks)
    print(f"✅ {len(chunks)} chunks PDF ajoutés")
else:
    print("⚠️ Pas de test.pdf trouvé")

# ─── IMAGE ──────────────────────────────────────────
print("\n🖼️ Extraction Image...")
image_path = "backend/test.png"
if os.path.exists(image_path):
    image_text = extract_text_from_image(image_path)
    if image_text.strip():
        all_chunks.append(image_text)
        print(f"✅ Texte image ajouté")
    else:
        print("⚠️ Aucun texte détecté dans l'image")
else:
    print("⚠️ Pas de test.png trouvé")

# ─── UML ────────────────────────────────────────────
print("\n📊 Extraction UML...")
uml_path = "backend/test_uml.png"
if os.path.exists(uml_path):
    uml_text = extract_text_from_uml(uml_path)
    all_chunks.append(uml_text)
    print(f"✅ Description UML ajoutée")
else:
    print("⚠️ Pas de test_uml.png trouvé")

print(f"\n📦 Total : {len(all_chunks)} chunks à indexer")

# ─── INDEXATION ─────────────────────────────────────
print("\n🗄️ Indexation dans ChromaDB...")
index = create_index(
    chunks=all_chunks,
    metadata={"source": "multimodal", "type": "mixed"}
)

# ─── QUESTIONS ──────────────────────────────────────
print("\n💬 Système de questions prêt !")
print("Tapez 'exit' pour quitter\n")

query_engine = create_query_engine(index)

while True:
    question = input("Votre question : ")
    if question.lower() == "exit":
        break
    reponse = ask_question(query_engine, question)
    print(f"\n🤖 Réponse : {reponse}")
    print("-" * 50)

print("\n🎉 Tests terminés !")