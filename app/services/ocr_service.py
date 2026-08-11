from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def load_image_text(path: str) -> str:
    image = Image.open(path)
    image = image.convert("L")  # convert to grayscale

    text = pytesseract.image_to_string(image)
    return text.strip()