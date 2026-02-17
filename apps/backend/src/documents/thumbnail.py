"""
Thumbnail generation for image documents (JPG, PNG).

Pillow (PIL) resizes images to a configurable max size. Returns thumbnail bytes
for storage; does not write to disk.
"""
from io import BytesIO
from typing import BinaryIO


def generate_thumbnail(
    file_obj: BinaryIO | None = None,
    content_type: str = "",
    max_size: tuple[int, int] = (200, 200),
) -> tuple[bytes | None, int]:
    """
    Generate thumbnail bytes for an image file (JPG, PNG).

    Returns (thumbnail_bytes, size). For non-image types (e.g. PDF), returns (None, 0).
    """
    if not file_obj or content_type not in ("image/jpeg", "image/png"):
        return None, 0
    try:
        from PIL import Image
    except ImportError:
        return None, 0
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        out = BytesIO()
        img.save(out, format="PNG")
        data = out.getvalue()
        return data, len(data)
    except Exception:
        return None, 0
