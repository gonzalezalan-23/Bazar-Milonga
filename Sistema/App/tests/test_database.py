import sys
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database


class SharedDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_path = database.DB_PATH
        database.DB_PATH = Path(self.temp.name) / "demo.sqlite3"
        database.crear_tablas()

    def tearDown(self):
        database.DB_PATH = self.original_path
        self.temp.cleanup()

    def product(self, stock=5, price=1200):
        with database.conectar_db() as conn:
            return database.ingresar_producto(conn, "Brocha", "Maquillaje", stock, 500, price)

    def reserve(self, product_id, quantity=1):
        with database.conectar_db() as conn:
            return database.crear_reserva(conn, "Ana", "112233", "Retiro", "", [(product_id, quantity)])

    def test_product_create_and_update(self):
        with database.conectar_db() as conn:
            product_id = database.ingresar_producto(conn, "Brocha", "Maquillaje", 2, 400, 900)
            same_id = database.ingresar_producto(conn, "brocha", "maquillaje", 3, 450, 1000)
            row = conn.execute("SELECT * FROM productos WHERE id=?", (product_id,)).fetchone()
        self.assertEqual(product_id, same_id)
        self.assertEqual((5, 450, 1000), (row["stock"], row["precio_compra"], row["precio_venta"]))

    def test_invalid_category_and_nonpositive_sale_price_are_rejected(self):
        with database.conectar_db() as conn:
            with self.assertRaises(ValueError):
                database.ingresar_producto(conn, "Nuevo", "Categoría inventada", 2, 100, 500)
            with self.assertRaises(ValueError):
                database.ingresar_producto(conn, "Nuevo", "Accesorios", 2, 100, 0)
            self.assertEqual(0, conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0])

    def test_sold_out_and_oversized_orders_do_not_change_inventory(self):
        product_id = self.product(stock=1)
        order_id = self.reserve(product_id, 1)
        with self.assertRaises(ValueError):
            self.reserve(product_id, 1)
        with self.assertRaises(ValueError):
            self.reserve(product_id, 2)
        with database.conectar_db() as conn:
            self.assertEqual(0, conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()[0])
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM pedidos_web").fetchone()[0])
            self.assertGreater(order_id, 0)

    def test_two_orders_competing_for_last_unit(self):
        product_id = self.product(stock=1)
        barrier = threading.Barrier(2)
        outcomes = []
        def request():
            barrier.wait()
            try:
                outcomes.append(("ok", self.reserve(product_id)))
            except ValueError:
                outcomes.append(("unavailable", None))
        threads = [threading.Thread(target=request) for _ in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=15)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertCountEqual(["ok", "unavailable"], [result[0] for result in outcomes])
        with database.conectar_db() as conn:
            self.assertEqual(0, conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()[0])
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM pedidos_web").fetchone()[0])

    def test_cancel_replenishes_once_and_order_is_visible_and_advanceable(self):
        product_id = self.product(stock=4)
        order_id = self.reserve(product_id, 2)
        with database.conectar_db() as conn:
            order = conn.execute("SELECT * FROM pedidos_web WHERE id=?", (order_id,)).fetchone()
            items = conn.execute("SELECT * FROM pedido_web_items WHERE pedido_id=?", (order_id,)).fetchall()
            self.assertEqual("Ana", order["cliente"])
            self.assertEqual((1, 2), (len(items), items[0]["cantidad"]))
            self.assertTrue(database.cambiar_estado_pedido(conn, order_id, "En preparación"))
            self.assertTrue(database.cambiar_estado_pedido(conn, order_id, "Preparado"))
        with database.conectar_db() as conn:
            self.assertTrue(database.cancelar_reserva(conn, order_id))
        with database.conectar_db() as conn:
            self.assertFalse(database.cancelar_reserva(conn, order_id))
            self.assertEqual(4, conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()[0])
            self.assertEqual("Cancelado", conn.execute("SELECT estado FROM pedidos_web WHERE id=?", (order_id,)).fetchone()[0])

    def test_delivered_order_cannot_be_cancelled_or_restore_stock(self):
        product_id = self.product(stock=3)
        order_id = self.reserve(product_id, 1)
        with database.conectar_db() as conn:
            self.assertFalse(database.cambiar_estado_pedido(conn, order_id, "Entregado"))
            self.assertTrue(database.cambiar_estado_pedido(conn, order_id, "En preparación"))
        with database.conectar_db() as conn:
            self.assertTrue(database.cambiar_estado_pedido(conn, order_id, "Preparado"))
        with database.conectar_db() as conn:
            self.assertTrue(database.cambiar_estado_pedido(conn, order_id, "Entregado"))
        with database.conectar_db() as conn:
            self.assertFalse(database.cancelar_reserva(conn, order_id))
            self.assertEqual(2, conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()[0])

    def test_local_sale_records_items_and_decrements_stock_atomically(self):
        product_id = self.product(stock=5, price=1200)
        with database.conectar_db() as conn:
            sale_id, total = database.registrar_venta_local(conn, [(product_id, 2)], "Débito")
        with database.conectar_db() as conn:
            product = conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()
            sale = conn.execute("SELECT total,metodo_pago FROM ventas WHERE id=?", (sale_id,)).fetchone()
            item = conn.execute("SELECT cantidad,nombre_producto,precio_unitario FROM venta_items WHERE venta_id=?", (sale_id,)).fetchone()
            movement = conn.execute("SELECT tipo,cantidad,stock_resultante FROM movimientos_stock WHERE producto_id=? ORDER BY id DESC LIMIT 1", (product_id,)).fetchone()
        self.assertEqual(2400, total)
        self.assertEqual(3, product["stock"])
        self.assertEqual((2400, "Débito"), (sale["total"], sale["metodo_pago"]))
        self.assertEqual((2, "Brocha", 1200), (item["cantidad"], item["nombre_producto"], item["precio_unitario"]))
        self.assertEqual(("Venta local", -2, 3), (movement["tipo"], movement["cantidad"], movement["stock_resultante"]))

    def test_sale_without_stock_does_not_create_sale(self):
        product_id = self.product(stock=1)
        with self.assertRaises(ValueError):
            with database.conectar_db() as conn:
                database.registrar_venta_local(conn, [(product_id, 2)])
        with database.conectar_db() as conn:
            self.assertEqual(1, conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()[0])
            self.assertEqual(0, conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0])

    def test_category_management_and_stock_adjustment_are_audited(self):
        with database.conectar_db() as conn:
            self.assertEqual("Papelería", database.agregar_categoria(conn, "  Papelería  "))
            with self.assertRaises(ValueError):
                database.agregar_categoria(conn, "papelería")
            self.assertIn("Papelería", database.listar_categorias(conn))
            product_id = database.ingresar_producto(conn, "Cuaderno", "Papelería", 4, 100, 250)
            database.ajustar_stock(conn, product_id, 6, "Conteo físico")
            movement = conn.execute("SELECT tipo,cantidad,stock_resultante,detalle FROM movimientos_stock WHERE producto_id=? ORDER BY id DESC LIMIT 1", (product_id,)).fetchone()
        self.assertEqual(("Ajuste", 2, 6, "Conteo físico"), (movement["tipo"], movement["cantidad"], movement["stock_resultante"], movement["detalle"]))

    def test_voiding_sale_restores_stock_once_and_keeps_history(self):
        product_id = self.product(stock=3)
        with database.conectar_db() as conn:
            sale_id, _ = database.registrar_venta_local(conn, [(product_id, 2)])
        with database.conectar_db() as conn:
            self.assertTrue(database.anular_venta_local(conn, sale_id))
        with database.conectar_db() as conn:
            self.assertFalse(database.anular_venta_local(conn, sale_id))
            self.assertEqual(3, conn.execute("SELECT stock FROM productos WHERE id=?", (product_id,)).fetchone()[0])
            self.assertEqual("Anulada", conn.execute("SELECT estado FROM ventas WHERE id=?", (sale_id,)).fetchone()[0])
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM venta_items WHERE venta_id=?", (sale_id,)).fetchone()[0])

    def test_schema_migration_preserves_existing_products_and_sales(self):
        old_path = database.DB_PATH
        legacy = Path(self.temp.name) / "legacy.sqlite3"
        connection = sqlite3.connect(legacy)
        connection.executescript("""
            CREATE TABLE productos(id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, categoria TEXT, stock INTEGER NOT NULL DEFAULT 0, precio_compra REAL, precio_venta REAL NOT NULL DEFAULT 0);
            INSERT INTO productos(id,nombre,categoria,stock,precio_compra,precio_venta) VALUES(7,'Vincha','Accesorios',45,1000,3999);
            CREATE TABLE ventas(id INTEGER PRIMARY KEY, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, total REAL NOT NULL DEFAULT 0, metodo_pago TEXT);
            INSERT INTO ventas(id,total,metodo_pago) VALUES(3,1200,'Efectivo');
        """)
        connection.close()
        try:
            database.DB_PATH = legacy
            database.crear_tablas()
            database.crear_tablas()
            with database.conectar_db() as conn:
                product = conn.execute("SELECT nombre,stock,imagen,descripcion FROM productos WHERE id=7").fetchone()
                sale = conn.execute("SELECT total,estado FROM ventas WHERE id=3").fetchone()
                movements = conn.execute("SELECT COUNT(*) FROM movimientos_stock WHERE producto_id=7 AND tipo='Saldo inicial'").fetchone()[0]
                # Nuevas columnas/tablas deben existir
                cols = {row[1] for row in conn.execute("PRAGMA table_info(movimientos_stock)")}
                self.assertIn("costo_unitario", cols)
                conn.execute("SELECT COUNT(*) FROM gastos")
            self.assertEqual(("Vincha", 45, None, None), tuple(product))
            self.assertEqual((1200, "Registrada"), tuple(sale))
            self.assertEqual(1, movements)
        finally:
            database.DB_PATH = old_path


class BalanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_path = database.DB_PATH
        database.DB_PATH = Path(self.temp.name) / "balance.sqlite3"
        database.crear_tablas()

    def tearDown(self):
        database.DB_PATH = self.original_path
        self.temp.cleanup()

    def _producto(self, compra=500, venta=1200):
        with database.conectar_db() as conn:
            return database.ingresar_producto(conn, "Art", "Accesorios", 10, compra, venta)

    def test_balance_venta_local_excluye_anuladas(self):
        pid = self._producto()
        with database.conectar_db() as conn:
            sid, _ = database.registrar_venta_local(conn, [(pid, 2)])
        with database.conectar_db() as conn:
            database.anular_venta_local(conn, sid)
        with database.conectar_db() as conn:
            # Forzar fecha del mes actual
            import datetime
            mes = datetime.date.today()
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(0, b["ingresos_local"])

    def test_balance_venta_local_registrada(self):
        pid = self._producto(venta=1000)
        with database.conectar_db() as conn:
            database.registrar_venta_local(conn, [(pid, 3)])
        import datetime
        mes = datetime.date.today()
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(3000, b["ingresos_local"])

    def test_balance_pedido_web_excluye_no_entregados_y_cancelados(self):
        pid = self._producto()
        with database.conectar_db() as conn:
            oid = database.crear_reserva(conn, "Ana", "111", "Retiro", "", [(pid, 1)])
        import datetime
        mes = datetime.date.today()
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(0, b["ingresos_web"])  # pendiente, no entregado
        with database.conectar_db() as conn:
            database.cancelar_reserva(conn, oid)
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(0, b["ingresos_web"])  # cancelado

    def test_balance_pedido_web_entregado(self):
        pid = self._producto(venta=800)
        with database.conectar_db() as conn:
            oid = database.crear_reserva(conn, "Ana", "111", "Retiro", "", [(pid, 2)])
            database.cambiar_estado_pedido(conn, oid, "En preparación")
            database.cambiar_estado_pedido(conn, oid, "Preparado")
            database.cambiar_estado_pedido(conn, oid, "Entregado")
        import datetime
        mes = datetime.date.today()
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(1600, b["ingresos_web"])

    def test_balance_egresos_compras_usa_costo_del_movimiento(self):
        # Ingreso con costo 500 x 4 unidades
        with database.conectar_db() as conn:
            database.ingresar_producto(conn, "Prod", "Accesorios", 4, 500, 1000)
        import datetime
        mes = datetime.date.today()
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        # 4 unidades a 500 = 2000 (solo movimientos con costo_unitario)
        self.assertEqual(2000, b["egresos_compras"])

    def test_balance_egresos_compras_ignora_movimientos_sin_costo(self):
        """Movimientos legacy sin costo_unitario no se suman."""
        import datetime
        mes = datetime.date.today()
        prefijo = f"{mes.year:04d}-{mes.month:02d}-15"
        with database.conectar_db() as conn:
            conn.execute(
                "INSERT INTO movimientos_stock(tipo,cantidad,stock_resultante,detalle,fecha) VALUES('Ingreso',5,5,'Legacy',?)",
                (prefijo,),
            )
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(0, b["egresos_compras"])

    def test_registrar_gasto_y_aparece_en_balance(self):
        import datetime
        mes = datetime.date.today()
        fecha = mes.isoformat()
        with database.conectar_db() as conn:
            database.registrar_gasto(conn, fecha, "Bolsas", 350)
            database.registrar_gasto(conn, fecha, "Flete", 150)
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        self.assertEqual(500, b["egresos_gastos"])

    def test_registrar_gasto_validaciones(self):
        with database.conectar_db() as conn:
            with self.assertRaises(ValueError):
                database.registrar_gasto(conn, "15-06-2025", "Desc", 100)  # formato incorrecto
            with self.assertRaises(ValueError):
                database.registrar_gasto(conn, "2025-06-15", "", 100)  # sin descripción
            with self.assertRaises(ValueError):
                database.registrar_gasto(conn, "2025-06-15", "Desc", 0)  # importe cero
            with self.assertRaises(ValueError):
                database.registrar_gasto(conn, "2025-06-15", "Desc", -50)  # importe negativo
            self.assertEqual(0, conn.execute("SELECT COUNT(*) FROM gastos").fetchone()[0])

    def test_balance_neto_suma_correctamente(self):
        import datetime
        mes = datetime.date.today()
        pid = self._producto(compra=400, venta=1000)
        with database.conectar_db() as conn:
            database.registrar_venta_local(conn, [(pid, 2)])  # +2000
            database.registrar_gasto(conn, mes.isoformat(), "Gasto", 300)  # -300
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, mes.year, mes.month)
        # ingresos_local=2000, egresos_compras=10*400=4000 (ingreso inicial), egresos_gastos=300
        self.assertEqual(b["ingresos_local"] + b["ingresos_web"] - b["egresos"], b["balance"])

    def test_balance_mes_sin_datos_devuelve_ceros(self):
        with database.conectar_db() as conn:
            b = database.calcular_balance(conn, 2000, 1)
        self.assertEqual({"ingresos_local": 0, "ingresos_web": 0, "egresos_compras": 0,
                          "egresos_gastos": 0, "egresos": 0, "balance": 0}, b)

    def test_migracion_aditiva_preserva_datos_y_agrega_columnas(self):
        """crear_tablas() es idempotente y agrega costo_unitario y tabla gastos sin borrar datos."""
        pid = self._producto()
        database.crear_tablas()  # segunda llamada
        with database.conectar_db() as conn:
            self.assertIsNotNone(conn.execute("SELECT id FROM productos WHERE id=?", (pid,)).fetchone())
            cols = {row[1] for row in conn.execute("PRAGMA table_info(movimientos_stock)")}
            self.assertIn("costo_unitario", cols)
            conn.execute("SELECT COUNT(*) FROM gastos")


if __name__ == "__main__":
    unittest.main()
