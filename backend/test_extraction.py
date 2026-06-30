import sys
import os

# Ajoute backend au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extraction.pdf_loader import extract_text_from_pdf, split_into_chunks
from extraction.image_loader import extract_text_from_image
from extraction.uml_loader import extract_text_from_uml

# ─── TEST PDF ───────────────────────────────────────
print("=" * 40)
print("TEST PDF")
print("=" * 40)

# Mets le chemin d'un vrai PDF que tu as sur ton PC
pdf_path = "test.pdf"

if os.path.exists(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(text)
    print(f"Texte extrait : {len(text)} caractères")
    print(f"Nombre de chunks : {len(chunks)}")
    print(f"Premier chunk : {chunks[0][:200]}...")
else:
    print("Mets un fichier test.pdf dans rag-assistant/")

# ─── TEST IMAGE ─────────────────────────────────────
print("\n" + "=" * 40)
print("TEST IMAGE")
print("=" * 40)

image_path = "test.png"

if os.path.exists(image_path):
    text = extract_text_from_image(image_path)
    print(f"Texte extrait : {text[:300]}")
else:
    print("Mets un fichier test.png dans rag-assistant/")

# ─── TEST UML ───────────────────────────────────────
print("\n" + "=" * 40)
print("TEST UML")
print("=" * 40)

uml_path = "test_uml.png"

if os.path.exists(uml_path):
    description = extract_text_from_uml(uml_path)
    print(f"Description générée :\n{description[:500]}")
else:
    print("Mets un fichier test_uml.png dans rag-assistant/")

print("\n:)) Tests terminés !")