"""SQLite compartido por la app de escritorio y la tienda web."""
from contextlib import contextmanager
from pathlib import Path
import math
import sqlite3

DB_PATH = Path(__file__).resolve().with_name("milonga_datos.db")
ESTADOS_PEDIDO = ("Pendiente de coordinación", "En preparación", "Preparado", "Entregado", "Cancelado")
CATEGORIAS_PRODUCTO = ("Accesorios", "Electrónica", "Hogar", "Maquillaje", "Muebles", "Skincare", "Otros")


@contextmanager
def conectar_db():
    """Abre la base junto a este módulo, independientemente del cwd, y la cierra al salir."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def crear_tablas():
    with conectar_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, categoria TEXT,
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0), precio_compra REAL,
            precio_venta REAL NOT NULL DEFAULT 0)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0, metodo_pago TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS pedidos_web (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            cliente TEXT NOT NULL, telefono TEXT NOT NULL, entrega TEXT NOT NULL, comentario TEXT,
            total REAL NOT NULL, estado TEXT NOT NULL DEFAULT 'Pendiente de coordinación')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS pedido_web_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL REFERENCES pedidos_web(id),
            producto_id INTEGER NOT NULL REFERENCES productos(id), nombre_producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0), precio_unitario REAL NOT NULL)""")
        # Migraciones aditivas: conservan los productos y pedidos que ya existen.
        columnas = {row[1] for row in conn.execute("PRAGMA table_info(productos)")}
        if "imagen" not in columnas:
            conn.execute("ALTER TABLE productos ADD COLUMN imagen TEXT")
        if "descripcion" not in columnas:
            conn.execute("ALTER TABLE productos ADD COLUMN descripcion TEXT")
        ventas_columnas = {row[1] for row in conn.execute("PRAGMA table_info(ventas)")}
        if "estado" not in ventas_columnas:
            conn.execute("ALTER TABLE ventas ADD COLUMN estado TEXT NOT NULL DEFAULT 'Registrada'")
        conn.execute("CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL COLLATE NOCASE UNIQUE)")
        for categoria in CATEGORIAS_PRODUCTO:
            conn.execute("INSERT OR IGNORE INTO categorias(nombre) VALUES(?)", (categoria,))
        conn.execute("INSERT OR IGNORE INTO categorias(nombre) SELECT DISTINCT TRIM(categoria) FROM productos WHERE categoria IS NOT NULL AND TRIM(categoria)<>''")
        conn.execute("""CREATE TABLE IF NOT EXISTS movimientos_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT, producto_id INTEGER REFERENCES productos(id),
            fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL, stock_resultante INTEGER, detalle TEXT)""")
        conn.execute("""INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle)
            SELECT p.id,'Saldo inicial',p.stock,p.stock,'Inventario previo a activar historial'
            FROM productos p WHERE NOT EXISTS (SELECT 1 FROM movimientos_stock m WHERE m.producto_id=p.id)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS venta_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, venta_id INTEGER NOT NULL REFERENCES ventas(id),
            producto_id INTEGER REFERENCES productos(id), nombre_producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK(cantidad > 0), precio_unitario REAL NOT NULL)""")
        # Migración: costo_unitario en movimientos_stock (NULL para movimientos anteriores)
        mov_columnas = {row[1] for row in conn.execute("PRAGMA table_info(movimientos_stock)")}
        if "costo_unitario" not in mov_columnas:
            conn.execute("ALTER TABLE movimientos_stock ADD COLUMN costo_unitario REAL")
        # Tabla de gastos manuales
        conn.execute("""CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            importe REAL NOT NULL CHECK(importe > 0))""")


def registrar_gasto(conn, fecha, descripcion, importe):
    """Registra un gasto manual. fecha: str ISO 'YYYY-MM-DD', importe > 0."""
    import math as _math
    fecha = fecha.strip()
    descripcion = descripcion.strip()[:300]
    if not fecha or len(fecha) != 10 or fecha[4] != "-" or fecha[7] != "-":
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")
    try:
        import datetime as _dt
        _dt.date.fromisoformat(fecha)
    except ValueError:
        raise ValueError("La fecha ingresada no es válida.")
    if not descripcion:
        raise ValueError("Ingresá una descripción para el gasto.")
    try:
        importe = float(importe)
    except (TypeError, ValueError):
        raise ValueError("El importe debe ser un número mayor que cero.")
    if not _math.isfinite(importe) or importe <= 0:
        raise ValueError("El importe debe ser un número mayor que cero.")
    conn.execute(
        "INSERT INTO gastos(fecha, descripcion, importe) VALUES(?,?,?)",
        (fecha, descripcion, round(importe, 2)),
    )


def calcular_balance(conn, anio, mes):
    """Devuelve dict con ingresos_local, ingresos_web, egresos_compras, egresos_gastos, balance para el mes dado."""
    prefijo = f"{anio:04d}-{mes:02d}"
    # Ingresos ventas locales (excluye Anuladas)
    row = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM ventas WHERE estado='Registrada' AND strftime('%Y-%m',fecha)=?",
        (prefijo,),
    ).fetchone()
    ingresos_local = float(row[0])
    # Ingresos pedidos web entregados
    row = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM pedidos_web WHERE estado='Entregado' AND strftime('%Y-%m',fecha)=?",
        (prefijo,),
    ).fetchone()
    ingresos_web = float(row[0])
    # Egresos por ingresos de mercadería (solo movimientos con costo_unitario registrado)
    row = conn.execute(
        "SELECT COALESCE(SUM(cantidad * costo_unitario),0) FROM movimientos_stock "
        "WHERE tipo='Ingreso' AND costo_unitario IS NOT NULL AND strftime('%Y-%m',fecha)=?",
        (prefijo,),
    ).fetchone()
    egresos_compras = float(row[0])
    # Egresos por gastos manuales
    row = conn.execute(
        "SELECT COALESCE(SUM(importe),0) FROM gastos WHERE strftime('%Y-%m',fecha)=?",
        (prefijo,),
    ).fetchone()
    egresos_gastos = float(row[0])
    egresos = egresos_compras + egresos_gastos
    return {
        "ingresos_local": ingresos_local,
        "ingresos_web": ingresos_web,
        "egresos_compras": egresos_compras,
        "egresos_gastos": egresos_gastos,
        "egresos": egresos,
        "balance": ingresos_local + ingresos_web - egresos,
    }


def ingresar_producto(conn, nombre, categoria, cantidad, compra, venta, descripcion=None):
    nombre, categoria = nombre.strip(), (categoria.strip() or "Otros")
    categoria_existente = conn.execute("SELECT 1 FROM categorias WHERE nombre=? COLLATE NOCASE LIMIT 1", (categoria,)).fetchone()
    if not categoria_existente:
        # Compatibilidad con callers anteriores; toda categoría queda registrada.
        if categoria not in CATEGORIAS_PRODUCTO:
            raise ValueError("Agregá primero esa categoría desde Administrar categorías.")
        conn.execute("INSERT OR IGNORE INTO categorias(nombre) VALUES(?)", (categoria,))
    if not nombre or not isinstance(cantidad, int) or cantidad < 0 or not all(math.isfinite(float(v)) and float(v) >= 0 for v in (compra, venta)) or float(venta) <= 0:
        raise ValueError("Ingresá un nombre, cantidad válida, costo no negativo y precio de venta mayor que cero.")
    actual = conn.execute("SELECT id FROM productos WHERE nombre=? COLLATE NOCASE AND COALESCE(categoria,'')=? COLLATE NOCASE", (nombre, categoria)).fetchone()
    if actual:
        conn.execute("UPDATE productos SET stock=stock+?,precio_compra=?,precio_venta=?,descripcion=COALESCE(NULLIF(?,''),descripcion) WHERE id=?", (cantidad, compra, venta, (descripcion or "").strip()[:300], actual["id"]))
        nuevo_stock = conn.execute("SELECT stock FROM productos WHERE id=?", (actual["id"],)).fetchone()[0]
        if cantidad:
            conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle,costo_unitario) VALUES(?,?,?,?,?,?)", (actual["id"], "Ingreso", cantidad, nuevo_stock, "Ingreso de mercadería", compra))
        return actual["id"]
    product_id = conn.execute("INSERT INTO productos(nombre,categoria,stock,precio_compra,precio_venta,descripcion) VALUES(?,?,?,?,?,?)", (nombre,categoria,cantidad,compra,venta,(descripcion or "").strip()[:300])).lastrowid
    if cantidad:
        conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle,costo_unitario) VALUES(?,?,?,?,?,?)", (product_id, "Ingreso", cantidad, cantidad, "Stock inicial", compra))
    return product_id


def listar_categorias(conn):
    return [row[0] for row in conn.execute("SELECT nombre FROM categorias ORDER BY nombre COLLATE NOCASE")]


def agregar_categoria(conn, nombre):
    nombre = " ".join(nombre.split())
    if not nombre or len(nombre) > 40:
        raise ValueError("La categoría debe tener entre 1 y 40 caracteres.")
    try:
        conn.execute("INSERT INTO categorias(nombre) VALUES(?)", (nombre,))
    except sqlite3.IntegrityError as error:
        raise ValueError("Ya existe una categoría con ese nombre.") from error
    return nombre


def registrar_venta_local(conn, items, metodo_pago="Efectivo"):
    cantidades = {}
    for product_id, cantidad in items:
        if not isinstance(product_id, int) or not isinstance(cantidad, int) or cantidad < 1:
            raise ValueError("Revisá los productos y las cantidades de la venta.")
        cantidades[product_id] = cantidades.get(product_id, 0) + cantidad
    if not cantidades:
        raise ValueError("Agregá al menos un producto a la venta.")
    conn.execute("BEGIN IMMEDIATE")
    seleccionados, total = [], 0.0
    for product_id, cantidad in cantidades.items():
        product = conn.execute("SELECT id,nombre,stock,precio_venta FROM productos WHERE id=?", (product_id,)).fetchone()
        if not product or product["stock"] < cantidad or product["precio_venta"] <= 0:
            raise ValueError("No hay stock suficiente. Actualizá el inventario antes de cobrar.")
        seleccionados.append((product, cantidad)); total += product["precio_venta"] * cantidad
    venta_id = conn.execute("INSERT INTO ventas(total,metodo_pago) VALUES(?,?)", (total, metodo_pago)).lastrowid
    for product, cantidad in seleccionados:
        conn.execute("UPDATE productos SET stock=stock-? WHERE id=?", (cantidad, product["id"]))
        stock = conn.execute("SELECT stock FROM productos WHERE id=?", (product["id"],)).fetchone()[0]
        conn.execute("INSERT INTO venta_items(venta_id,producto_id,nombre_producto,cantidad,precio_unitario) VALUES(?,?,?,?,?)", (venta_id, product["id"], product["nombre"], cantidad, product["precio_venta"]))
        conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle) VALUES(?,?,?,?,?)", (product["id"], "Venta local", -cantidad, stock, f"Venta #{venta_id}"))
    return venta_id, total


def ajustar_stock(conn, product_id, nuevo_stock, detalle="Ajuste manual"):
    if not isinstance(nuevo_stock, int) or nuevo_stock < 0:
        raise ValueError("El stock debe ser un entero no negativo.")
    row = conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()
    if not row:
        raise ValueError("El producto ya no existe.")
    delta = nuevo_stock - row["stock"]
    conn.execute("UPDATE productos SET stock=? WHERE id=?", (nuevo_stock, product_id))
    if delta:
        conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle) VALUES(?,?,?,?,?)", (product_id, "Ajuste", delta, nuevo_stock, detalle[:200]))


def anular_venta_local(conn, sale_id):
    """Anula la venta completa, devuelve unidades una sola vez y conserva el registro."""
    conn.execute("BEGIN IMMEDIATE")
    sale = conn.execute("SELECT estado FROM ventas WHERE id=?", (sale_id,)).fetchone()
    if not sale or sale["estado"] != "Registrada":
        return False
    items = conn.execute("SELECT producto_id,cantidad FROM venta_items WHERE venta_id=?", (sale_id,)).fetchall()
    if not items:
        return False
    for item in items:
        if item["producto_id"] is not None:
            conn.execute("UPDATE productos SET stock=stock+? WHERE id=?", (item["cantidad"], item["producto_id"]))
            stock = conn.execute("SELECT stock FROM productos WHERE id=?", (item["producto_id"],)).fetchone()[0]
            conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle) VALUES(?,?,?,?,?)", (item["producto_id"], "Anulación de venta", item["cantidad"], stock, f"Venta #{sale_id}"))
    conn.execute("UPDATE ventas SET estado='Anulada' WHERE id=?", (sale_id,))
    return True


def crear_reserva(conn, cliente, telefono, entrega, comentario, items):
    """Crea una reserva y descuenta stock de forma atómica; items son (producto_id, cantidad)."""
    cantidades = {}
    for product_id, cantidad in items:
        if not isinstance(product_id, int) or not isinstance(cantidad, int) or cantidad < 1 or cantidad > 99:
            raise ValueError("Hay una cantidad inválida en el pedido.")
        cantidades[product_id] = cantidades.get(product_id, 0) + cantidad
        if cantidades[product_id] > 99: raise ValueError("La cantidad solicitada es demasiado grande.")
    if not cliente.strip() or not telefono.strip() or not entrega.strip() or not cantidades:
        raise ValueError("Faltan datos de contacto o artículos.")
    conn.execute("BEGIN IMMEDIATE")
    selected=[]; total=0.0
    for product_id, cantidad in cantidades.items():
        product=conn.execute("SELECT id,nombre,stock,precio_venta FROM productos WHERE id=?",(product_id,)).fetchone()
        if not product or product["stock"]<cantidad or product["precio_venta"]<=0:
            raise ValueError("Cambió la disponibilidad de un producto. Actualizá el catálogo e intentá de nuevo.")
        selected.append((product,cantidad));total+=product["precio_venta"]*cantidad
    order_id=conn.execute("INSERT INTO pedidos_web(cliente,telefono,entrega,comentario,total) VALUES(?,?,?,?,?)",(cliente.strip(),telefono.strip(),entrega.strip(),comentario[:1000],total)).lastrowid
    for product,cantidad in selected:
        changed=conn.execute("UPDATE productos SET stock=stock-? WHERE id=? AND stock>=?",(cantidad,product["id"],cantidad)).rowcount
        if changed!=1: raise ValueError("No hay stock suficiente para completar el pedido.")
        conn.execute("INSERT INTO pedido_web_items(pedido_id,producto_id,nombre_producto,cantidad,precio_unitario) VALUES(?,?,?,?,?)",(order_id,product["id"],product["nombre"],cantidad,product["precio_venta"]))
        stock = conn.execute("SELECT stock FROM productos WHERE id=?", (product["id"],)).fetchone()[0]
        conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle) VALUES(?,?,?,?,?)", (product["id"], "Reserva web", -cantidad, stock, f"Pedido #{order_id}"))
    return order_id


def cambiar_estado_pedido(conn, order_id, estado):
    transiciones = {
        "En preparación": ("Pendiente de coordinación",),
        "Preparado": ("Pendiente de coordinación", "En preparación"),
        "Entregado": ("Preparado",),
    }
    anteriores = transiciones.get(estado)
    if not anteriores:
        raise ValueError("Estado de pedido inválido.")
    placeholders = ",".join("?" for _ in anteriores)
    sql = f"UPDATE pedidos_web SET estado=? WHERE id=? AND estado IN ({placeholders})"
    return conn.execute(sql, (estado, order_id, *anteriores)).rowcount == 1


def cancelar_reserva(conn, order_id):
    """Cancela solo una vez y restituye las cantidades en la misma transacción."""
    conn.execute("BEGIN IMMEDIATE")
    pedido=conn.execute("SELECT estado FROM pedidos_web WHERE id=?",(order_id,)).fetchone()
    if not pedido or pedido["estado"] not in ("Pendiente de coordinación","En preparación","Preparado"):
        return False
    items=conn.execute("SELECT producto_id,cantidad FROM pedido_web_items WHERE pedido_id=?",(order_id,)).fetchall()
    for item in items:
        conn.execute("UPDATE productos SET stock=stock+? WHERE id=?",(item["cantidad"],item["producto_id"]))
        stock = conn.execute("SELECT stock FROM productos WHERE id=?", (item["producto_id"],)).fetchone()[0]
        conn.execute("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle) VALUES(?,?,?,?,?)", (item["producto_id"], "Cancelación de reserva", item["cantidad"], stock, f"Pedido #{order_id}"))
    conn.execute("UPDATE pedidos_web SET estado='Cancelado' WHERE id=?",(order_id,))
    return True
