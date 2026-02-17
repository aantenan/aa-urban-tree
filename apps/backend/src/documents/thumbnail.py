"""
Thumbnail generation for image documents.

Pillow (PIL) is used for resizing JPG/PNG files. This module provides
the interface for thumbnail creation; the actual generation logic is
implemented in a separate work order.

Usage (when implemented):
    from documents.thumbnail import generate_thumbnail
    thumb_path, thumb_size = generate_thumbnail(source_path, max_size=(200, 200))
"""
from typing import BinaryIO

# Pillow is available for thumbnail generation
try:
    from PIL import Image  # noqa: F401
except ImportError:
    Image = None  # type: ignore


def generate_thumbnail(
    source_path: str | None = None,
    file_obj: BinaryIO | None = None,
    content_type: str = "",
    max_size: tuple[int, int] = (200, 200),
) -> tuple[str | None, int]:
    """
    Generate thumbnail for an image file. Placeholder—implementation out of scope.

    Returns (thumbnail_path_or_none, thumbnail_size_bytes).
    For non-image types (e.g. PDF), returns (None, 0).
    """
    # Placeholder: thumbnail generation logic to be implemented separately
    _ = source_path, file_obj, content_type, max_size
    return None, 0
