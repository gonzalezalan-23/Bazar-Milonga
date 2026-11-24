"""Configuración local que la tienda web lee como JSON estático."""
import json
import re
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parents[1] / "Web"
CONFIG_PATH = WEB_DIR / "tienda.json"
SAFE_IMAGE = re.compile(r"^uploads/[A-Za-z0-9._-]+$")


def leer_configuracion():
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    address = data.get("direccion", "") if isinstance(data, dict) else ""
    image = data.get("imagen_portada", "") if isinstance(data, dict) else ""
    return {
        "direccion": address.strip()[:240] if isinstance(address, str) else "",
        "imagen_portada": image if isinstance(image, str) and SAFE_IMAGE.fullmatch(image) else "",
    }


def guardar_configuracion(direccion, imagen_portada):
    direccion = " ".join(direccion.split())
    imagen_portada = (imagen_portada or "").strip()
    if len(direccion) > 240:
        raise ValueError("La dirección puede tener hasta 240 caracteres.")
    if imagen_portada and not SAFE_IMAGE.fullmatch(imagen_portada):
        raise ValueError("La ruta de la imagen de portada no es válida.")
    data = {"direccion": direccion, "imagen_portada": imagen_portada}
    temporary = CONFIG_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CONFIG_PATH)
    return data
