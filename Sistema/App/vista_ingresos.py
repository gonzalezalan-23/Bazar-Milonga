import math
import sqlite3
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from database import agregar_categoria, conectar_db, ingresar_producto, listar_categorias
from image_utils import guardar_foto
from ui_components import SafeOptionMenu

MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}


class VistaIngresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="Ingresos", font=("Arial", 30, "bold"), text_color="#30232B").pack(anchor="w", pady=(0, 16))
        form = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=15)
        form.pack(fill="both", expand=True)
        ctk.CTkLabel(form, text="Registrar producto o ingreso de stock", font=("Arial", 19, "bold"), text_color="#713D54").pack(anchor="w", padx=30, pady=(22, 4))
        ctk.CTkLabel(form, text="Escribí para ver coincidencias. Elegir un producto existente suma las unidades; si no elegís una sugerencia, se crea un producto nuevo.", font=("Arial", 14), text_color="#51454D", wraplength=760, justify="left").pack(anchor="w", padx=30, pady=(0, 8))
        self._suggest_job = None
        self._suspend_suggestions = False
        self._metadata_product_id = None
        self.nombre_var = ctk.StringVar(master=self, value="")
        self.nombre = self.campo(form, "Nombre del artículo", "Ej. Vincha skincare gatito", variable=self.nombre_var)
        self.nombre_var.trace_add("write", self.programar_sugerencias)
        self.nombre.bind("<KeyRelease>", self.manejar_tecla_sugerencias)
        self.sugerencias = ctk.CTkFrame(self.nombre.master, fg_color="#FCF8F9", corner_radius=8)
        self.descripcion = self.campo(form, "Descripción para la tienda (opcional)", "Ej. Vincha de tela suave, varios colores")
        category_box = ctk.CTkFrame(form, fg_color="transparent")
        category_box.pack(fill="x", padx=30, pady=7)
        ctk.CTkLabel(category_box, text="Categoría", text_color="#30232B", font=("Arial", 14, "bold")).pack(anchor="w")
        category_actions = ctk.CTkFrame(category_box, fg_color="transparent")
        category_actions.pack(fill="x", pady=(5, 0))
        self.categoria = SafeOptionMenu(category_actions, values=["Accesorios"], height=46, fg_color="#F4E9EE", button_color="#A64F72", button_hover_color="#873B5A", text_color="#30232B", dropdown_fg_color="#FFFCFB", dropdown_hover_color="#EBD5DE", dropdown_text_color="#30232B", font=("Arial", 14), dropdown_font=("Arial", 14))
        self.categoria.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(category_actions, text="Agregar categoría", width=160, height=46, fg_color="#F4E9EE", hover_color="#EBD5DE", text_color="#713D54", font=("Arial", 13, "bold"), command=self.nueva_categoria).pack(side="right")
        self.actualizar_categorias()
        self.cantidad = self.campo(form, "Unidades que ingresan", "Ej. 5")
        self.compra = self.campo(form, "Precio de compra por unidad ($)", "Ej. 500")
        self.venta = self.campo(form, "Precio de venta por unidad ($)", "Ej. 1200")
        image_box = ctk.CTkFrame(form, fg_color="transparent")
        image_box.pack(fill="x", padx=30, pady=8)
        ctk.CTkLabel(image_box, text="Foto del producto (opcional)", text_color="#30232B", font=("Arial", 14, "bold")).pack(anchor="w")
        image_row = ctk.CTkFrame(image_box, fg_color="transparent")
        image_row.pack(fill="x", pady=(5, 0))
        self.image_path = None
        self.image_label = ctk.CTkLabel(image_row, text="Sin foto", anchor="w", text_color="#51454D", font=("Arial", 13))
        self.image_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(image_row, text="Elegir imagen…", height=42, width=150, fg_color="#F4E9EE", hover_color="#EBD5DE", text_color="#713D54", command=self.elegir_imagen).pack(side="right")
        ctk.CTkLabel(form, text="Formatos JPG, PNG o WebP · máximo 8 MB · el precio de venta debe ser mayor que cero.", font=("Arial", 12), text_color="#51454D", wraplength=700).pack(anchor="w", padx=30, pady=(3, 0))
        ctk.CTkButton(form, text="Guardar en inventario", fg_color="#A64F72", hover_color="#873B5A", text_color="white", height=50, font=("Arial", 15, "bold"), command=self.guardar).pack(fill="x", padx=30, pady=(14, 24))

    def campo(self, parent, titulo, placeholder, variable=None):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", padx=30, pady=6)
        ctk.CTkLabel(box, text=titulo, text_color="#30232B", font=("Arial", 14, "bold")).pack(anchor="w")
        entry = ctk.CTkEntry(box, placeholder_text=placeholder, height=46, fg_color="#FCF8F9", border_color="#A9939E", text_color="#30232B", placeholder_text_color="#675762", font=("Arial", 14), textvariable=variable)
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def actualizar_categorias(self, seleccionar=None):
        try:
            with conectar_db() as conn:
                values = listar_categorias(conn)
        except sqlite3.Error:
            values = ["Accesorios", "Otros"]
        self.categoria.configure(values=values or ["Otros"])
        actual = seleccionar or (self.categoria.get() if hasattr(self, "categoria") else "Accesorios")
        self.categoria.set(actual if actual in values else (values[0] if values else "Otros"))

    def nueva_categoria(self):
        dialog = ctk.CTkInputDialog(text="Nombre de la nueva categoría:", title="Agregar categoría")
        nombre = dialog.get_input()
        if not nombre:
            return
        try:
            with conectar_db() as conn:
                nombre = agregar_categoria(conn, nombre)
            self.actualizar_categorias(nombre)
        except ValueError as error:
            messagebox.showerror("No se pudo agregar", str(error), parent=self)
        except sqlite3.Error as error:
            messagebox.showerror("Error de base de datos", str(error), parent=self)

    def programar_sugerencias(self, *_args):
        if self._suspend_suggestions:
            return
        if self._metadata_product_id is not None:
            for entry in (self.descripcion, self.compra, self.venta):
                entry.delete(0, "end")
            self.image_path = None
            self.image_label.configure(text="Sin foto")
        self._metadata_product_id = None
        if self._suggest_job:
            try:
                self.after_cancel(self._suggest_job)
            except Exception:
                pass
        self._suggest_job = self.after(100, self.sugerir)

    def manejar_tecla_sugerencias(self, event):
        if event.keysym == "Escape":
            self.sugerencias.pack_forget()
            return "break"
        if event.keysym not in ("Down", "Up", "Return"):
            return
        buttons = self.sugerencias.winfo_children()
        if not buttons:
            return
        focused = self.focus_get()
        try:
            index = buttons.index(focused)
        except ValueError:
            index = -1
        if event.keysym == "Return":
            if event.widget is self.nombre or event.widget is getattr(self.nombre, "_entry", None):
                buttons[0].invoke()
        else:
            next_index = 0 if index < 0 else (index + (1 if event.keysym == "Down" else -1)) % len(buttons)
            buttons[next_index].focus_set()
        return "break"

    def destroy(self):
        if self._suggest_job:
            try:
                self.after_cancel(self._suggest_job)
            except Exception:
                pass
            self._suggest_job = None
        super().destroy()

    def sugerir(self):
        self._suggest_job = None
        query = self.nombre.get().strip()
        for child in self.sugerencias.winfo_children():
            child.destroy()
        if len(query) < 2:
            self.sugerencias.pack_forget()
            return
        try:
            with conectar_db() as conn:
                exactos = conn.execute("SELECT id,nombre,categoria,stock,precio_compra,precio_venta,descripcion,imagen FROM productos WHERE nombre=? COLLATE NOCASE ORDER BY id LIMIT 2", (query,)).fetchall()
                rows = conn.execute("SELECT id,nombre,categoria,stock,precio_compra,precio_venta,descripcion,imagen FROM productos WHERE nombre LIKE ? ORDER BY CASE WHEN nombre=? COLLATE NOCASE THEN 0 WHEN nombre LIKE ? THEN 1 ELSE 2 END,nombre COLLATE NOCASE LIMIT 8", (f"%{query}%", query, f"{query}%")).fetchall()
        except sqlite3.Error as error:
            self.mostrar_estado_sugerencias(f"No se pudo buscar en el inventario: {error}")
            return
        if len(exactos) == 1:
            self.autocompletar_producto(exactos[0])
            self.sugerencias.pack_forget()
            return
        if not rows:
            self.mostrar_estado_sugerencias("No hay coincidencias. Al guardar, se creará un producto nuevo.")
            return
        self.sugerencias.pack(fill="x", pady=(4, 0))
        for row in rows:
            label = f"{row['nombre']}  ·  {row['categoria'] or 'Otros'}  ·  {row['stock']} en stock"
            button = ctk.CTkButton(self.sugerencias, text=label, anchor="w", height=40, fg_color="transparent", hover_color="#EBD5DE", text_color="#30232B", font=("Arial", 14), command=lambda value=row: self.seleccionar_sugerencia(value))
            button.pack(fill="x", padx=5, pady=2)
            button.bind("<KeyRelease>", self.manejar_tecla_sugerencias)

    def mostrar_estado_sugerencias(self, texto):
        for child in self.sugerencias.winfo_children():
            child.destroy()
        ctk.CTkLabel(self.sugerencias, text=texto, anchor="w", justify="left", wraplength=700, font=("Arial", 13), text_color="#51454D").pack(fill="x", padx=10, pady=9)
        self.sugerencias.pack(fill="x", pady=(4, 0))

    def autocompletar_producto(self, product):
        self._suspend_suggestions = True
        try:
            if self.nombre.get() != product["nombre"]:
                self.nombre_var.set(product["nombre"])
            self.categoria.set(product["categoria"] or "Otros")
            self.descripcion.delete(0, "end")
            self.descripcion.insert(0, product["descripcion"] or "")
            self.compra.delete(0, "end")
            self.compra.insert(0, str(product["precio_compra"] or 0))
            self.venta.delete(0, "end")
            self.venta.insert(0, str(product["precio_venta"]))
            self.image_path = None
            self.image_label.configure(text="Foto actual cargada" if product["imagen"] else "Sin foto")
            self._metadata_product_id = product["id"]
        finally:
            self._suspend_suggestions = False

    def seleccionar_sugerencia(self, product):
        self._suspend_suggestions = True
        try:
            self.nombre_var.set(product["nombre"])
        finally:
            self._suspend_suggestions = False
        self.autocompletar_producto(product)
        self.sugerencias.pack_forget()

    def elegir_imagen(self):
        path = filedialog.askopenfilename(parent=self, title="Elegir foto del producto", filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
        if not path:
            return
        image = Path(path)
        if image.suffix.lower() not in IMAGE_TYPES or image.stat().st_size > MAX_IMAGE_BYTES:
            messagebox.showerror("Imagen no válida", "Elegí un archivo JPG, PNG o WebP de hasta 8 MB.", parent=self)
            return
        self.image_path = image
        self.image_label.configure(text=image.name)

    def guardar(self):
        if self._suggest_job:
            try:
                self.after_cancel(self._suggest_job)
            except Exception:
                pass
            self._suggest_job = None
        self.sugerir()
        nombre = self.nombre.get().strip()
        categoria = self.categoria.get()
        try:
            cantidad = int(self.cantidad.get())
            compra = float(self.compra.get().replace(",", "."))
            venta = float(self.venta.get().replace(",", "."))
            if not nombre or cantidad < 0 or not all(math.isfinite(x) and x >= 0 for x in (compra, venta)) or venta <= 0:
                raise ValueError
            with conectar_db() as conn:
                product_id = ingresar_producto(conn, nombre, categoria, cantidad, compra, venta, self.descripcion.get().strip())
                if self.image_path:
                    image_ref = guardar_foto(self.image_path, product_id)
                    conn.execute("UPDATE productos SET imagen=? WHERE id=?", (image_ref, product_id))
        except ValueError as error:
            messagebox.showerror("Revisá los datos", str(error) or "Ingresá un nombre, cantidad entera no negativa, costo no negativo y precio de venta mayor que cero. La foto debe ser JPG, PNG o WebP de hasta 8 MB.", parent=self)
            return
        except (sqlite3.Error, OSError) as error:
            messagebox.showerror("No se pudo guardar", f"Revisá la base o el archivo de imagen: {error}", parent=self)
            return
        for entry in (self.nombre, self.descripcion, self.cantidad, self.compra, self.venta):
            entry.delete(0, "end")
        self.image_path = None
        self.image_label.configure(text="Sin foto")
        self.sugerencias.pack_forget()
        messagebox.showinfo("Inventario actualizado", f"{nombre}: ingreso guardado en {categoria}.", parent=self)
