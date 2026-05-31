"""
Image export utilities.
"""

import numpy as np
from pathlib import Path
from typing import Optional


def export_image(rgba: np.ndarray, file_path: str,
                quality: int = 95) -> bool:
    """
    Export an RGBA image array to a file.

    Args:
        rgba: RGBA image array (height, width, 4), uint8
        file_path: Output file path
        quality: JPEG quality (only used for .jpg files)

    Returns:
        True if successful

    Raises:
        ValueError: If image format is invalid
        IOError: If file cannot be written
    """
    if rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError("Image must be RGBA format (height, width, 4)")

    if rgba.dtype != np.uint8:
        rgba = np.clip(rgba, 0, 255).astype(np.uint8)

    path = Path(file_path)
    suffix = path.suffix.lower()

    # Try to use PIL/Pillow first (best quality)
    try:
        from PIL import Image

        # Convert RGBA to PIL Image
        img = Image.fromarray(rgba, mode='RGBA')

        if suffix in ('.jpg', '.jpeg'):
            # JPEG doesn't support alpha, convert to RGB
            img = img.convert('RGB')
            img.save(file_path, quality=quality)
        else:
            img.save(file_path)

        return True
    except ImportError:
        pass

    # Fall back to PyQt6 if PIL not available
    try:
        from PyQt6.QtGui import QImage

        height, width = rgba.shape[:2]
        qimage = QImage(
            rgba.data.tobytes(),
            width, height,
            width * 4,
            QImage.Format.Format_RGBA8888
        )

        if suffix in ('.jpg', '.jpeg'):
            # Convert to RGB for JPEG
            qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)

        success = qimage.save(file_path, quality=quality)
        if not success:
            raise IOError(f"Failed to save image to {file_path}")

        return True
    except ImportError:
        pass

    # Last resort: save as raw PPM (always works)
    if suffix not in ('.ppm', '.pgm'):
        # Change extension
        path = path.with_suffix('.ppm')
        file_path = str(path)

    height, width = rgba.shape[:2]
    rgb = rgba[:, :, :3]  # Drop alpha

    with open(file_path, 'wb') as f:
        # PPM header
        f.write(f"P6\n{width} {height}\n255\n".encode())
        # Raw RGB data
        f.write(rgb.tobytes())

    return True


def get_supported_formats() -> list:
    """
    Get list of supported export formats.

    Returns:
        List of format tuples (name, extension)
    """
    formats = [
        ("PNG Image", ".png"),
        ("PPM Image", ".ppm"),
    ]

    # Check for additional format support
    try:
        from PIL import Image
        formats.insert(1, ("JPEG Image", ".jpg"))
        formats.insert(2, ("BMP Image", ".bmp"))
        formats.insert(3, ("TIFF Image", ".tiff"))
    except ImportError:
        pass

    return formats
