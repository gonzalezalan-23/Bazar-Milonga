# Milonga Bazar

Sistema de gestión de inventario y tienda local para un bazar. Desarrollado como proyecto integrador para la materia de programación.

Tiene dos partes que comparten una base de datos SQLite:

- **App de escritorio** (`Sistema/App/`) — Python con CustomTkinter. Gestiona productos, stock, ventas locales, pedidos web y balance.
- **Tienda web local** (`Sistema/Web/`) — PHP + HTML/CSS/JS. Muestra el catálogo y recibe reservas. Funciona solo en la computadora local con un servidor PHP; no está pensada para publicarse en Internet.

---

## Estructura del proyecto

```
Bazar/
├── Sistema/
│   ├── App/
│   │   ├── main.py               # Punto de entrada de la app de escritorio
│   │   ├── database.py           # Capa de datos SQLite compartida con la web
│   │   ├── vista_stock.py        # Vista: stock actual
│   │   ├── vista_ingresos.py     # Vista: ingreso de mercadería
│   │   ├── vista_ventas.py       # Vista: ventas locales y pedidos web
│   │   ├── vista_avisos.py       # Vista: avisos de stock bajo
│   │   ├── vista_balance.py      # Vista: balance mensual e ingresos/egresos
│   │   ├── store_config.py       # Lectura/escritura de tienda.json
│   │   ├── image_utils.py        # Redimensionado y guardado de fotos
│   │   ├── ui_components.py      # Componentes de UI reutilizables
│   │   ├── milonga_datos.db      # Base de datos SQLite (compartida con la web)
│   │   ├── requirements.txt      # Dependencias Python
│   │   └── tests/
│   │       └── test_database.py  # Pruebas unitarias de la capa de datos
│   ├── Web/
│   │   ├── index.html            # Tienda web (SPA)
│   │   ├── app.js                # Lógica del catálogo y carrito
│   │   ├── styles.css            # Estilos
│   │   ├── api.php               # API REST mínima (productos y reservas)
│   │   ├── index.php             # Redirige a index.html en Apache
│   │   ├── tienda.json           # Dirección y foto de portada del local
│   │   ├── assets/               # Logo
│   │   ├── templates/            # Plantillas PHP alternativas
│   │   └── uploads/              # Fotos de productos y portada
│   ├── MANUAL-USUARIO.md         # Manual de uso detallado
│   └── LEEME-LOCAL.txt           # Instrucciones rápidas de arranque
└── README.md
```

---

## Requisitos

**App de escritorio**
- Python 3.11 o superior
- Las dependencias están en `Sistema/App/requirements.txt`:
  - `customtkinter >= 5.2, < 6`
  - `Pillow >= 10.0, < 14` (opcional, para redimensionar fotos)

**Tienda web**
- PHP 8.1 o superior con la extensión `pdo_sqlite` habilitada
- XAMPP es la forma más sencilla de tenerlo en Windows

---

## Instalación y ejecución

### App de escritorio

```powershell
cd Sistema\App
python -m pip install -r requirements.txt
python main.py
```

### Tienda web local

En otra ventana de PowerShell:

```powershell
cd Sistema\Web
C:\xampp\php\php.exe -S 127.0.0.1:8000
```

Abrí `http://127.0.0.1:8000/` en el navegador. Para detener el servidor, presioná `Ctrl+C` en esa ventana.

La tienda lee la base de datos directamente desde `Sistema/App/milonga_datos.db`. Ambos programas deben apuntar a la misma carpeta.

---

## Funcionalidades principales

| Sección | Descripción |
|---|---|
| Stock actual | Lista de productos con búsqueda, edición, historial de movimientos y retiro del catálogo |
| Avisos | Productos con stock bajo o agotado |
| Ingresos | Alta de productos nuevos y reposición de unidades con autocompletado |
| Ventas y pedidos | Registro de ventas de mostrador e historial; gestión de reservas recibidas desde la tienda web |
| Balance | Resumen mensual de ingresos (ventas locales + pedidos entregados) y egresos (compras + gastos manuales) para los últimos 3 meses |
| Tienda web | Catálogo público con carrito y formulario de reserva |

---

## Base de datos

La base SQLite se crea y migra automáticamente al iniciar la app. Las migraciones son aditivas: nunca borran datos existentes. Las tablas principales son:

- `productos` — catálogo con stock, precios y foto
- `movimientos_stock` — historial de cada cambio de stock, con `costo_unitario` guardado en el momento del ingreso
- `ventas` + `venta_items` — ventas locales
- `pedidos_web` + `pedido_web_items` — reservas de la tienda
- `gastos` — gastos manuales para el balance
- `categorias` — categorías administrables

---

## Pruebas

```powershell
cd Sistema\App
python -m unittest discover -s tests -v
```

Las pruebas cubren: creación y actualización de productos, concurrencia en reservas, cancelaciones, ventas locales, anulaciones, cálculos de balance por mes, exclusión de estados (anuladas, canceladas, no entregadas), gastos manuales, validaciones e idempotencia de migraciones.

---

## Notas técnicas

- La tienda web **no funciona en GitHub Pages** ni en ningún hosting estático porque requiere PHP y acceso al archivo SQLite local.
- El servidor PHP integrado (`php -S`) es solo para desarrollo/uso local. No usar en producción ni exponer en red.
- `preferencias.json` (escala de la interfaz) se genera localmente y está excluido del repositorio.
- Las fotos de productos se guardan en `Sistema/Web/uploads/` y la base guarda solo la ruta relativa.
