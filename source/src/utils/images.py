import os
import shutil

from fastapi import UploadFile
from PIL import Image

STATIC_DIR = "static/images"
MAX_IMAGE_SIZE = (300, 200)

os.makedirs(STATIC_DIR, exist_ok=True)


async def save_product_image(file: UploadFile, article: str) -> str:
    file_extension = file.filename.split(".")[-1]
    filename = f"{article}.{file_extension}"
    file_path = os.path.join(STATIC_DIR, filename)

    temp_path = f"{file_path}.temp"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with Image.open(temp_path) as img:
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            img.save(file_path, "JPEG", quality=85)

        os.remove(temp_path)
        return filename
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e


def delete_product_image(filename: str) -> bool:
    if not filename:
        return False

    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def get_image_path(filename: str | None) -> str:
    if filename and os.path.exists(os.path.join(STATIC_DIR, filename)):
        return f"/static/images/{filename}"
    return "/static/images/picture.png"
