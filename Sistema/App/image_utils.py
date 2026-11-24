"""Helpers para guardar fotos pequeñas y aptas para el catálogo local."""
from pathlib import Path
from uuid import uuid4
import shutil

WEB_UPLOADS = Path(__file__).resolve().parents[1] / "Web" / "uploads"
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 8 * 1024 * 1024
MAX_EDGE = 1600


def guardar_foto(source, product_id):
    source = Path(source)
    if source.suffix.lower() not in SUPPORTED:
        raise ValueError("Elegí una imagen JPG, PNG o WebP.")
    if source.stat().st_size > MAX_BYTES:
        raise ValueError("La imagen supera el límite de 8 MB.")
    WEB_UPLOADS.mkdir(parents=True, exist_ok=True)
    suffix = source.suffix.lower()
    filename = f"{product_id}-{uuid4().hex}{suffix}"
    destination = WEB_UPLOADS / filename
    try:
        from PIL import Image
        with Image.open(source) as image:
            image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
            if suffix in (".jpg", ".jpeg"):
                image.convert("RGB").save(destination, quality=88, optimize=True)
            elif suffix == ".webp":
                image.save(destination, quality=88, method=6)
            else:
                image.save(destination, optimize=True)
    except ImportError:
        shutil.copy2(source, destination)
    except Exception as error:
        destination.unlink(missing_ok=True)
        raise ValueError(f"No se pudo procesar la imagen: {error}") from error
    return f"uploads/{filename}"
