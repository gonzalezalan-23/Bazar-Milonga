import math
import sqlite3
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from database import ajustar_stock, conectar_db
from image_utils import guardar_foto

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}


class VistaStock(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="Stock actual", font=("Arial", 29, "bold"), text_color="#30232B").pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self, text="Buscá, corregí precios y revisá el historial de movimientos.", font=("Arial", 14), text_color="#51454D").pack(anchor="w", pady=(0, 14))
        self.card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.card.pack(fill="both", expand=True)
        self.search = ctk.CTkEntry(self.card, placeholder_text="Buscar por producto o categoría", height=46, fg_color="#FCF8F9", border_color="#A9939E", text_color="#30232B", placeholder_text_color="#675762", font=("Arial", 14))
        self.search.pack(fill="x", padx=20, pady=(18, 8))
        self.search.bind("<KeyRelease>", self.programar_busqueda)
        self.rows = ctk.CTkScrollableFrame(self.card, fg_color="transparent")
        self.rows.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self._search_job = None
        self.page_size = 300
        self.page_offset = 0
        self.more_button = None
        self.cargar_productos()

    def programar_busqueda(self, _event=None):
        if self._search_job:
            self.after_cancel(self._search_job)
        self.page_offset = 0
        self._search_job = self.after(180, self.cargar_productos)

    def cargar_productos(self, siguiente=False):
        self._search_job = None
        if not siguiente:
            self.page_offset = 0
            for widget in self.rows.winfo_children():
                widget.destroy()
        elif self.more_button:
            self.more_button.destroy()
            self.more_button = None
        query = self.search.get().strip()
        try:
            with conectar_db() as conn:
                productos = conn.execute("SELECT id,nombre,categoria,stock,precio_venta,descripcion FROM productos WHERE nombre LIKE ? OR categoria LIKE ? ORDER BY nombre COLLATE NOCASE LIMIT ? OFFSET ?", (f"%{query}%", f"%{query}%", self.page_size + 1, self.page_offset)).fetchall()
        except sqlite3.Error as error:
            ctk.CTkLabel(self.rows, text=f"No se pudo leer el inventario: {error}", text_color="#8B344D", wraplength=600).pack(pady=35)
            return
        if not productos and self.page_offset == 0:
            ctk.CTkLabel(self.rows, text="No hay productos que coincidan. Probá otro nombre o cargá un artículo desde Ingresos.", text_color="#51454D", wraplength=620, justify="center", font=("Arial", 14)).pack(pady=40)
            return
        hay_mas = len(productos) > self.page_size
        productos = productos[:self.page_size]
        for product in productos:
            row = ctk.CTkFrame(self.rows, fg_color="#FFFCFB", corner_radius=9, border_width=1, border_color="#E6DCE1")
            row.pack(fill="x", pady=4)
            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(fill="x", padx=14, pady=(10, 4))
            ctk.CTkLabel(details, text=product["nombre"], anchor="w", wraplength=400, text_color="#30232B", font=("Arial", 15, "bold")).pack(side="left", fill="x", expand=True)
            stock_color = "#8B344D" if product["stock"] == 0 else "#30232B"
            ctk.CTkLabel(details, text=f"{product['stock']} u.  ·  $ {product['precio_venta']:,.0f}".replace(",", "."), text_color=stock_color, font=("Arial", 14, "bold")).pack(side="right", padx=(6, 0))
            ctk.CTkLabel(row, text=product["categoria"] or "Otros", text_color="#51454D", font=("Arial", 12)).pack(anchor="w", padx=14, pady=(0, 6))
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(fill="x", padx=10, pady=(0, 8))
            ctk.CTkButton(actions, text="Editar", width=86, height=38, fg_color="#A64F72", hover_color="#873B5A", text_color="white", font=("Arial", 13), command=lambda p=product: self.editar(p)).pack(side="left", padx=3)
            ctk.CTkButton(actions, text="Movimientos", width=125, height=38, fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", font=("Arial", 13), command=lambda p=product: self.historial(p)).pack(side="left", padx=3)
            ctk.CTkButton(actions, text="Retirar del catálogo", width=160, height=38, fg_color="#F7E9E8", hover_color="#EED7D5", text_color="#713D54", font=("Arial", 13), command=lambda p=product: self.borrar(p)).pack(side="right", padx=3)
        self.page_offset += len(productos)
        if hay_mas:
            self.more_button = ctk.CTkButton(self.rows, text="Cargar los próximos productos", height=42, fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", font=("Arial", 14, "bold"), command=lambda: self.cargar_productos(siguiente=True))
            self.more_button.pack(fill="x", pady=8)

    def editar(self, product):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar producto")
        dialog.geometry("460x530")
        dialog.minsize(440, 490)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Editar {product['nombre']}", font=("Arial", 20, "bold"), text_color="#30232B", wraplength=390).pack(anchor="w", padx=24, pady=(20, 5))
        ctk.CTkLabel(dialog, text="Los cambios de stock quedan anotados en Movimientos.", font=("Arial", 13), text_color="#51454D").pack(anchor="w", padx=24, pady=(0, 10))
        stock_entry = self.edit_field(dialog, "Unidades disponibles", str(product["stock"]))
        price_entry = self.edit_field(dialog, "Precio de venta ($)", str(product["precio_venta"]))
        description_entry = self.edit_field(dialog, "Descripción de la tienda (opcional)", product["descripcion"] or "")
        image_row = ctk.CTkFrame(dialog, fg_color="transparent")
        image_row.pack(fill="x", padx=24, pady=8)
        selected_image = {"path": None}
        image_label = ctk.CTkLabel(image_row, text="Cambiar foto (opcional)", text_color="#51454D", font=("Arial", 13))
        image_label.pack(side="left", fill="x", expand=True)
        def choose_image():
            filename = filedialog.askopenfilename(parent=dialog, filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
            if filename:
                candidate = Path(filename)
                if candidate.suffix.lower() not in IMAGE_TYPES or candidate.stat().st_size > 8 * 1024 * 1024:
                    messagebox.showerror("Imagen no válida", "Elegí JPG, PNG o WebP de hasta 8 MB.", parent=dialog)
                    return
                selected_image["path"] = candidate
                image_label.configure(text=candidate.name)
        ctk.CTkButton(image_row, text="Elegir foto…", width=130, height=40, fg_color="#F4E9EE", hover_color="#EBD5DE", text_color="#713D54", command=choose_image).pack(side="right")
        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(fill="x", padx=24, pady=(12, 20))
        ctk.CTkButton(buttons, text="Cancelar", fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", height=42, command=dialog.destroy).pack(side="right", padx=(8, 0))
        def guardar():
            try:
                stock = int(stock_entry.get())
                price = float(price_entry.get().replace(",", "."))
                if stock < 0 or not math.isfinite(price) or price <= 0:
                    raise ValueError
                with conectar_db() as conn:
                    ajustar_stock(conn, product["id"], stock)
                    conn.execute("UPDATE productos SET precio_venta=?,descripcion=? WHERE id=?", (price, description_entry.get().strip()[:300], product["id"]))
                    if selected_image["path"]:
                        path = selected_image["path"]
                        image_ref = guardar_foto(path, product["id"])
                        conn.execute("UPDATE productos SET imagen=? WHERE id=?", (image_ref, product["id"]))
            except ValueError:
                messagebox.showerror("Dato inválido", "El stock debe ser entero no negativo y el precio mayor que cero.", parent=dialog)
                return
            except (sqlite3.Error, OSError, ValueError) as error:
                messagebox.showerror("No se pudo actualizar", str(error), parent=dialog)
                return
            dialog.destroy()
            self.cargar_productos()
        ctk.CTkButton(buttons, text="Guardar cambios", fg_color="#A64F72", hover_color="#873B5A", text_color="white", height=42, command=guardar).pack(side="right")
        stock_entry.focus_set()

    def edit_field(self, parent, title, value):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(box, text=title, font=("Arial", 14, "bold"), text_color="#30232B").pack(anchor="w")
        entry = ctk.CTkEntry(box, height=44, fg_color="#FCF8F9", border_color="#A9939E", text_color="#30232B", font=("Arial", 14))
        entry.insert(0, value)
        entry.pack(fill="x", pady=(4, 0))
        return entry

    def historial(self, product):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Movimientos · {product['nombre']}")
        dialog.geometry("640x480")
        dialog.transient(self.winfo_toplevel())
        ctk.CTkLabel(dialog, text=f"Movimientos de {product['nombre']}", font=("Arial", 19, "bold"), text_color="#30232B", wraplength=570).pack(anchor="w", padx=20, pady=(18, 8))
        rows = ctk.CTkScrollableFrame(dialog, fg_color="white")
        rows.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        with conectar_db() as conn:
            movements = conn.execute("SELECT fecha,tipo,cantidad,stock_resultante,detalle FROM movimientos_stock WHERE producto_id=? ORDER BY id DESC LIMIT 200", (product["id"],)).fetchall()
        for movement in movements:
            ctk.CTkLabel(rows, text=f"{movement['fecha']}  ·  {movement['tipo']}  ·  {movement['cantidad']:+d} u.  ·  stock: {movement['stock_resultante']}\n{movement['detalle'] or ''}", anchor="w", justify="left", wraplength=550, font=("Arial", 13), text_color="#30232B").pack(fill="x", padx=8, pady=7)
        if not movements:
            ctk.CTkLabel(rows, text="Todavía no hay movimientos registrados.", font=("Arial", 14), text_color="#51454D").pack(pady=24)

    def borrar(self, product):
        if not messagebox.askyesno("Retirar producto", f"¿Retirar {product['nombre']} del catálogo? Se conservará su historial.", parent=self):
            return
        try:
            with conectar_db() as conn:
                ajustar_stock(conn, product["id"], 0, "Retiro del catálogo")
                conn.execute("UPDATE productos SET precio_venta=0 WHERE id=?", (product["id"],))
        except sqlite3.Error as error:
            messagebox.showerror("No se pudo retirar", f"La base de datos rechazó el cambio: {error}", parent=self)
        self.cargar_productos()
