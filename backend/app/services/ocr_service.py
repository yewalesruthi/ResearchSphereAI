import logging
from typing import Dict, Optional

import pytesseract
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)


def preprocess_image(image_path: str) -> Image.Image:
    img = Image.open(image_path)
    gray = img.convert("L")
    denoised = gray.filter(ImageFilter.MedianFilter(size=3))
    return denoised


def extract_text_from_image(image_path: str) -> str:
    processed = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed)
    return text.strip()


def extract_image_metadata(image_path: str) -> Dict[str, Optional[str]]:
    img = Image.open(image_path)
    exif = img.getexif()
    metadata: Dict[str, Optional[str]] = {
        "format": img.format,
        "mode": img.mode,
        "size": f"{img.width}x{img.height}",
    }
    if exif:
        for tag_id, value in exif.items():
            try:
                from PIL.ExifTags import TAGS

                tag = TAGS.get(tag_id, str(tag_id))
                metadata[str(tag)] = str(value)
            except Exception:
                continue
    return metadata
