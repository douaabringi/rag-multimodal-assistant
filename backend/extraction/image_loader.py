import pytesseract
from PIL import Image
import os

# Dis à pytesseract où est Tesseract sur Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(file_path: str) -> str:
    """
    Prend le chemin d'une image
    Retourne le texte détecté par OCR
    """
    # Ouvre l'image
    image = Image.open(file_path)
    
    # Lance l'OCR (détecte français et anglais)
    text = pytesseract.image_to_string(
        image, 
        lang='fra+eng'
    )
    
    return text


def preprocess_image(file_path: str) -> Image.Image:
    """
    Améliore la qualité de l'image avant OCR
    (utile pour les screenshots flous)
    """
    image = Image.open(file_path)
    
    # Convertit en noir et blanc (améliore l'OCR)
    image = image.convert('L')
    
    return image