import datetime
import sqlite3
import tkinter.messagebox as messagebox

import customtkinter as ctk

from database import calcular_balance, conectar_db, registrar_gasto

MESES_ES = ("", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")


def _ultimos_3_meses():
    hoy = datetime.date.today()
    meses = []
    for delta in range(2, -1, -1):
        mes = hoy.month - delta
        anio = hoy.year
        while mes < 1:
            mes += 12
            anio -= 1
        meses.append((anio, mes))
    return meses


def _fmt(valor):
    return f"$ {valor:,.0f}".replace(",", ".")


class VistaBalance(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.pack(fill="x", pady=(0, 14))
        title_box = ctk.CTkFrame(heading, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_box, text="Balance", font=("Arial", 30, "bold"), text_color="#30232B").pack(anchor="w", pady=(0, 3))
        ctk.CTkLabel(title_box, text="Resumen de ingresos y egresos de los últimos 3 meses.", font=("Arial", 13), text_color="#51454D").pack(anchor="w")
        ctk.CTkButton(heading, text="Registrar gasto", width=145, height=42, fg_color="#A64F72", hover_color="#873B5A", text_color="white", font=("Arial", 13, "bold"), command=self.nuevo_gasto).pack(side="right")
        self.card = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=15)
        self.card.configure(label_text="")
        self.card.pack(fill="both", expand=True)
        self.cargar()

    def cargar(self):
        for w in self.card.winfo_children():
            w.destroy()
        meses = _ultimos_3_meses()
        totales = {"ingresos_local": 0, "ingresos_web": 0, "egresos_compras": 0, "egresos_gastos": 0, "egresos": 0, "balance": 0}
        sin_costo = False
        try:
            with conectar_db() as conn:
                datos = [(anio, mes, calcular_balance(conn, anio, mes)) for anio, mes in meses]
                # Detectar si hay ingresos de mercadería sin costo registrado
                sin_costo = conn.execute(
                    "SELECT COUNT(*) FROM movimientos_stock WHERE tipo='Ingreso' AND costo_unitario IS NULL AND cantidad > 0"
                ).fetchone()[0] > 0
        except sqlite3.Error as error:
            ctk.CTkLabel(self.card, text=f"No se pudo cargar el balance: {error}", text_color="#8B344D", font=("Arial", 14)).pack(pady=30)
            return

        if sin_costo:
            aviso = ctk.CTkFrame(self.card, fg_color="#FFF3CD", corner_radius=8)
            aviso.pack(fill="x", padx=24, pady=(16, 4))
            ctk.CTkLabel(aviso, text="⚠ Hay ingresos de mercadería anteriores sin costo registrado. Esos movimientos no se incluyen en los egresos de compras.", wraplength=700, justify="left", font=("Arial", 13), text_color="#7A5C00").pack(anchor="w", padx=14, pady=10)

        for anio, mes, d in datos:
            for k in totales:
                totales[k] += d[k]
            self._fila_mes(anio, mes, d)

        # Totales del período
        sep = ctk.CTkFrame(self.card, fg_color="#D9CBD1", height=1)
        sep.pack(fill="x", padx=24, pady=(8, 0))
        self._fila_totales(totales)

    def _fila_mes(self, anio, mes, d):
        frame = ctk.CTkFrame(self.card, fg_color="#FFFCFB", corner_radius=10, border_width=1, border_color="#E6DCE1")
        frame.pack(fill="x", padx=24, pady=(14, 0))
        ctk.CTkLabel(frame, text=f"{MESES_ES[mes]} {anio}", font=("Arial", 16, "bold"), text_color="#713D54").pack(anchor="w", padx=16, pady=(12, 6))
        self._linea(frame, "Ventas locales", _fmt(d["ingresos_local"]), "#24533D")
        self._linea(frame, "Pedidos web entregados", _fmt(d["ingresos_web"]), "#24533D")
        self._linea(frame, "Compras de mercadería", _fmt(d["egresos_compras"]), "#713D54")
        self._linea(frame, "Gastos manuales", _fmt(d["egresos_gastos"]), "#713D54")
        sep = ctk.CTkFrame(frame, fg_color="#E6DCE1", height=1)
        sep.pack(fill="x", padx=16, pady=4)
        color_balance = "#24533D" if d["balance"] >= 0 else "#8B344D"
        self._linea(frame, "Balance neto", _fmt(d["balance"]), color_balance, bold=True, pady_bottom=12)

    def _fila_totales(self, d):
        frame = ctk.CTkFrame(self.card, fg_color="#F4E9EE", corner_radius=10)
        frame.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkLabel(frame, text="Total del período", font=("Arial", 16, "bold"), text_color="#30232B").pack(anchor="w", padx=16, pady=(12, 6))
        self._linea(frame, "Ventas locales", _fmt(d["ingresos_local"]), "#24533D")
        self._linea(frame, "Pedidos web entregados", _fmt(d["ingresos_web"]), "#24533D")
        self._linea(frame, "Compras de mercadería", _fmt(d["egresos_compras"]), "#713D54")
        self._linea(frame, "Gastos manuales", _fmt(d["egresos_gastos"]), "#713D54")
        sep = ctk.CTkFrame(frame, fg_color="#D9CBD1", height=1)
        sep.pack(fill="x", padx=16, pady=4)
        color_balance = "#24533D" if d["balance"] >= 0 else "#8B344D"
        self._linea(frame, "Balance neto", _fmt(d["balance"]), color_balance, bold=True, pady_bottom=12)

    def _linea(self, parent, label, valor, color, bold=False, pady_bottom=4):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, pady_bottom))
        font = ("Arial", 14, "bold") if bold else ("Arial", 14)
        ctk.CTkLabel(row, text=label, font=font, text_color="#30232B", anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=valor, font=font, text_color=color, anchor="e").pack(side="right")

    def nuevo_gasto(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Registrar gasto")
        dialog.geometry("480x320")
        dialog.minsize(420, 290)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Registrar gasto manual", font=("Arial", 20, "bold"), text_color="#30232B").pack(anchor="w", padx=24, pady=(20, 4))

        def campo(titulo, placeholder):
            box = ctk.CTkFrame(dialog, fg_color="transparent")
            box.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(box, text=titulo, font=("Arial", 14, "bold"), text_color="#30232B").pack(anchor="w")
            entry = ctk.CTkEntry(box, placeholder_text=placeholder, height=44, fg_color="#FCF8F9", border_color="#A9939E", text_color="#30232B", placeholder_text_color="#675762", font=("Arial", 14))
            entry.pack(fill="x", pady=(4, 0))
            return entry

        hoy = datetime.date.today().isoformat()
        fecha_entry = campo("Fecha (AAAA-MM-DD)", hoy)
        fecha_entry.insert(0, hoy)
        desc_entry = campo("Descripción", "Ej. Bolsas, fletes, servicios…")
        importe_entry = campo("Importe ($)", "Ej. 1500")

        status = ctk.CTkLabel(dialog, text="", font=("Arial", 13), text_color="#8B344D", wraplength=420)
        status.pack(anchor="w", padx=24)

        def guardar():
            try:
                with conectar_db() as conn:
                    registrar_gasto(conn, fecha_entry.get(), desc_entry.get(), importe_entry.get())
            except ValueError as error:
                status.configure(text=str(error))
                return
            except sqlite3.Error as error:
                messagebox.showerror("No se pudo guardar", str(error), parent=dialog)
                return
            dialog.destroy()
            self.cargar()
            messagebox.showinfo("Gasto registrado", "El gasto fue guardado correctamente.", parent=self)

        footer = ctk.CTkFrame(dialog, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(10, 20))
        ctk.CTkButton(footer, text="Cancelar", width=100, height=42, fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", command=dialog.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(footer, text="Guardar gasto", width=140, height=42, fg_color="#A64F72", hover_color="#873B5A", text_color="white", font=("Arial", 14, "bold"), command=guardar).pack(side="right")
