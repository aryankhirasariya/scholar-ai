from PIL import Image, ImageFilter, ImageEnhance
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image(image: Image.Image) -> Image.Image:
    # resize small images — Tesseract works best at 300+ DPI
    w, h = image.size
    if w < 1000:
        scale = 1000 / w
        image = image.resize(
            (int(w * scale), int(h * scale)),
            Image.LANCZOS
        )

    # convert to grayscale
    image = image.convert("L")

    # increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # sharpen
    image = image.filter(ImageFilter.SHARPEN)

    return image


def load_image_text(path: str) -> str:
    image = Image.open(path)
    image = preprocess_image(image)

    # use best OCR config for screenshots/documents
    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(image, config=custom_config)

    return text.strip()