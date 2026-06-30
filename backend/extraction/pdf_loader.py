import fitz  # PyMuPDF
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

def extract_text_from_pdf(file_path: str) -> str:
    """
    Prend le chemin d'un PDF
    Retourne tout le texte extrait
    """
    text = ""
    
    # Ouvre le PDF
    document = fitz.open(file_path)
    
    # Parcourt chaque page
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += f"\n--- Page {page_num + 1} ---\n"
        text += page.get_text()
    
    document.close()
    
    return text


def split_into_chunks(text: str, chunk_size: int = 512) -> list:
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=100
    )
    nodes = splitter.get_nodes_from_documents(
        [Document(text=text)]
    )
    return [node.get_content() for node in nodes]