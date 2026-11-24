import sqlite3
import tkinter.messagebox as messagebox

import customtkinter as ctk

from database import anular_venta_local, conectar_db, cancelar_reserva, cambiar_estado_pedido, registrar_venta_local
from ui_components import SafeOptionMenu


class VistaVentas(ctk.CTkFrame):
    """Bandeja de reservas recibidas desde la tienda."""
    ESTADOS = ("Pendiente de coordinación", "En preparación", "Preparado", "Cancelado")

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.pack(fill="x", pady=(0, 14))
        title_box = ctk.CTkFrame(heading, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_box, text="Ventas y pedidos", font=("Arial", 27, "bold"), text_color="#30232B").pack(anchor="w", pady=(0, 3))
        ctk.CTkLabel(title_box, text="Registrá ventas de mostrador y gestioná reservas de la tienda.", font=("Arial", 13), text_color="#51454D").pack(anchor="w")
        ctk.CTkButton(heading, text="Historial local", width=130, height=42, fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", font=("Arial", 13, "bold"), command=self.historial_local).pack(side="right", padx=(6, 0))
        ctk.CTkButton(heading, text="Nueva venta local", width=155, height=42, fg_color="#A64F72", hover_color="#873B5A", text_color="white", font=("Arial", 13, "bold"), command=self.nueva_venta).pack(side="right")
        self.card=ctk.CTkFrame(self,fg_color="white",corner_radius=15);self.card.pack(fill="both",expand=True)
        toolbar=ctk.CTkFrame(self.card,fg_color="transparent");toolbar.pack(fill="x",padx=20,pady=(16,8))
        ctk.CTkLabel(toolbar,text="Mostrar:",font=("Arial",13,"bold"),text_color="#30232B").pack(side="left",padx=(0,9))
        self.filter=SafeOptionMenu(toolbar,values=["Pendiente de coordinación",*self.ESTADOS[1:],"Todos"],command=lambda _value:self.cargar_pedidos(),fg_color="#F4E9EE",button_color="#A64F72",button_hover_color="#873B5A",text_color="#30232B",dropdown_fg_color="#FFFCFB",dropdown_hover_color="#EBD5DE",dropdown_text_color="#30232B",height=42,font=("Arial",14),dropdown_font=("Arial",14))
        self.filter.set("Pendiente de coordinación");self.filter.pack(side="left")
        ctk.CTkButton(toolbar,text="Actualizar pedidos",width=145,height=38,fg_color="#F4E9EE",hover_color="#E9D6DD",text_color="#713D54",font=("Arial",13,"bold"),command=self.cargar_pedidos).pack(side="right")
        self.summary=ctk.CTkLabel(self.card,text="",font=("Arial",12),text_color="#675762");self.summary.pack(anchor="w",padx=22,pady=(0,8))
        self.lista=ctk.CTkScrollableFrame(self.card,fg_color="transparent");self.lista.pack(fill="both",expand=True,padx=15,pady=(0,14))
        self.cargar_pedidos()

    def cargar_pedidos(self):
        for widget in self.lista.winfo_children():widget.destroy()
        estado=self.filter.get()
        try:
            with conectar_db() as conn:
                pending=conn.execute("SELECT COUNT(*) FROM pedidos_web WHERE estado='Pendiente de coordinación'").fetchone()[0]
                if estado=="Todos":pedidos=conn.execute("SELECT * FROM pedidos_web ORDER BY id DESC").fetchall()
                else:pedidos=conn.execute("SELECT * FROM pedidos_web WHERE estado=? ORDER BY id DESC",(estado,)).fetchall()
                self.summary.configure(text=f"{pending} pedido(s) pendiente(s) · Las unidades reservadas se descuentan del stock hasta marcar la entrega o cancelar el pedido.")
                if not pedidos:
                    text="No hay pedidos pendientes. Al recibir una reserva, va a aparecer acá." if estado=="Pendiente de coordinación" else "No hay pedidos en este filtro. Probá con ‘Todos’ para revisar el historial."
                    ctk.CTkLabel(self.lista,text=text,text_color="#51454D",font=("Arial",14),wraplength=650,justify="center").pack(pady=42)
                    self.actualizar_badge();return
                for pedido in pedidos:
                    items=conn.execute("SELECT nombre_producto,cantidad,precio_unitario FROM pedido_web_items WHERE pedido_id=? ORDER BY id",(pedido["id"],)).fetchall()
                    self.crear_tarjeta(pedido,items)
        except sqlite3.Error as error:
            self.summary.configure(text="No se pudieron actualizar los pedidos.")
            ctk.CTkLabel(self.lista,text=f"Problema con la base de datos: {error}",text_color="#8B344D",wraplength=620).pack(pady=35)
        self.actualizar_badge()

    def actualizar_badge(self):
        app=self.winfo_toplevel()
        if hasattr(app,"actualizar_badge_ventas"):app.actualizar_badge_ventas()

    def crear_tarjeta(self,pedido,items):
        card=ctk.CTkFrame(self.lista,fg_color="#FFFCFB",corner_radius=10,border_width=1,border_color="#E6DCE1");card.pack(fill="x",padx=5,pady=6)
        top=ctk.CTkFrame(card,fg_color="transparent");top.pack(fill="x",padx=16,pady=(12,5))
        ctk.CTkLabel(top,text=f"Pedido #{pedido['id']}",font=("Arial",16,"bold"),text_color="#30232B").pack(side="left")
        status_color={"Pendiente de coordinación":"#713D22","En preparación":"#24533D","Preparado":"#24533D","Entregado":"#24533D","Cancelado":"#713D54"}.get(pedido["estado"],"#30232B")
        ctk.CTkLabel(top,text=pedido["estado"],fg_color="#F4E9EE",corner_radius=14,text_color=status_color,font=("Arial",12,"bold"),height=30).pack(side="right",padx=4)
        customer=ctk.CTkFrame(card,fg_color="transparent");customer.pack(fill="x",padx=16,pady=3)
        ctk.CTkLabel(customer,text=f"{pedido['cliente']}  ·  {pedido['telefono']}",font=("Arial",14,"bold"),text_color="#30232B",anchor="w").pack(anchor="w")
        ctk.CTkLabel(customer,text=f"{pedido['fecha']}  ·  {pedido['entrega']}",font=("Arial",12),text_color="#51454D",anchor="w").pack(anchor="w",pady=(3,0))
        lines=[f"{item['cantidad']} × {item['nombre_producto']}  —  $ {item['precio_unitario']*item['cantidad']:,.0f}".replace(",",".") for item in items]
        ctk.CTkLabel(card,text="\n".join(lines) or "Sin detalle de productos",justify="left",anchor="w",font=("Arial",13),text_color="#51454D",wraplength=680).pack(fill="x",padx=16,pady=(8,3))
        ctk.CTkLabel(card,text=f"Total estimado: $ {pedido['total']:,.0f}".replace(",","."),font=("Arial",14,"bold"),text_color="#713D54").pack(anchor="w",padx=16,pady=(3,2))
        if pedido["comentario"]:
            ctk.CTkLabel(card,text=f"Consulta: {pedido['comentario']}",justify="left",wraplength=680,font=("Arial",12),text_color="#51454D").pack(anchor="w",padx=16,pady=(2,6))
        actions=ctk.CTkFrame(card,fg_color="transparent");actions.pack(fill="x",padx=12,pady=(8,12))
        state=pedido["estado"]
        if state=="Pendiente de coordinación":
            ctk.CTkButton(actions,text="Empezar preparación",width=170,height=38,fg_color="#A64F72",hover_color="#873B5A",text_color="white",font=("Arial",13,"bold"),command=lambda order_id=pedido["id"]:self.cambiar_estado(order_id,"En preparación")).pack(side="left",padx=4)
        if state in ("Pendiente de coordinación","En preparación"):
            ctk.CTkButton(actions,text="Marcar listo para entregar",width=190,height=38,fg_color="#3F7458",hover_color="#315D46",text_color="white",font=("Arial",13,"bold"),command=lambda order_id=pedido["id"]:self.cambiar_estado(order_id,"Preparado")).pack(side="left",padx=4)
        if state=="Preparado":
            ctk.CTkButton(actions,text="Marcar como entregado",width=190,height=38,fg_color="#3F7458",hover_color="#315D46",text_color="white",font=("Arial",13,"bold"),command=lambda order_id=pedido["id"]:self.cambiar_estado(order_id,"Entregado")).pack(side="left",padx=4)
        if state in ("Pendiente de coordinación","En preparación","Preparado"):
            ctk.CTkButton(actions,text="Cancelar y reponer stock",width=200,height=38,fg_color="#F7E9E8",hover_color="#EED7D5",text_color="#713D54",font=("Arial",13,"bold"),command=lambda order_id=pedido["id"]:self.cancelar_pedido(order_id)).pack(side="right",padx=4)

    def cambiar_estado(self,order_id,estado):
        try:
            with conectar_db() as conn:cambiado=cambiar_estado_pedido(conn,order_id,estado)
        except sqlite3.Error as error:
            messagebox.showerror("No se pudo actualizar",f"La base de datos rechazó el cambio: {error}",parent=self);return
        if not cambiado:messagebox.showinfo("Pedido actualizado","Ese pedido ya cambió de estado. Actualicé la lista.",parent=self)
        self.cargar_pedidos()

    def cancelar_pedido(self,order_id):
        if not messagebox.askyesno("Cancelar reserva",f"¿Cancelar el pedido #{order_id} y devolver sus unidades al stock?",parent=self):return
        try:
            with conectar_db() as conn:cancelado=cancelar_reserva(conn,order_id)
        except sqlite3.Error as error:
            messagebox.showerror("No se pudo cancelar",f"La base de datos rechazó la cancelación: {error}",parent=self);return
        if not cancelado:messagebox.showinfo("Pedido actualizado","Ese pedido ya cambió de estado. Actualicé la lista.",parent=self)
        self.cargar_pedidos()

    def nueva_venta(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva venta local")
        dialog.geometry("650x680")
        dialog.minsize(570, 600)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Venta de mostrador", font=("Arial", 22, "bold"), text_color="#30232B").pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(dialog, text="Buscá productos, agregalos a la venta y confirmá el cobro.", font=("Arial", 13), text_color="#51454D").pack(anchor="w", padx=22, pady=(0, 12))
        search = ctk.CTkEntry(dialog, placeholder_text="Buscar producto…", height=44, font=("Arial", 14), fg_color="#FCF8F9", border_color="#A9939E", text_color="#30232B")
        search.pack(fill="x", padx=22, pady=(0, 7))
        results = ctk.CTkScrollableFrame(dialog, height=175, fg_color="#FFFCFB")
        results.pack(fill="x", padx=22)
        cart_frame = ctk.CTkScrollableFrame(dialog, fg_color="white")
        cart_frame.pack(fill="both", expand=True, padx=22, pady=(12, 8))
        cart = {}
        status = ctk.CTkLabel(dialog, text="", font=("Arial", 13), text_color="#8B344D", wraplength=570)
        status.pack(anchor="w", padx=22)
        footer = ctk.CTkFrame(dialog, fg_color="transparent")
        footer.pack(fill="x", padx=22, pady=(8, 18))
        method = SafeOptionMenu(footer, values=["Efectivo", "Débito", "Crédito", "Transferencia", "Otro"], height=42, fg_color="#F4E9EE", button_color="#A64F72", button_hover_color="#873B5A", text_color="#30232B", dropdown_fg_color="#FFFCFB", dropdown_hover_color="#EBD5DE", dropdown_text_color="#30232B", font=("Arial", 13), dropdown_font=("Arial", 13))
        method.pack(side="left")
        total_label = ctk.CTkLabel(footer, text="Total: $ 0", font=("Arial", 17, "bold"), text_color="#30232B")
        total_label.pack(side="left", padx=14)

        def refresh_cart():
            for child in cart_frame.winfo_children(): child.destroy()
            total = 0
            for product_id, item in list(cart.items()):
                total += item["price"] * item["qty"]
                line = ctk.CTkFrame(cart_frame, fg_color="#FCF8F9", corner_radius=7)
                line.pack(fill="x", pady=3, padx=3)
                ctk.CTkLabel(line, text=f"{item['name']}  ·  {item['qty']} × $ {item['price']:,.0f}".replace(",", "."), anchor="w", font=("Arial", 13), text_color="#30232B").pack(side="left", fill="x", expand=True, padx=10, pady=9)
                ctk.CTkButton(line, text="−", width=36, height=34, fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", command=lambda pid=product_id: change_qty(pid, -1)).pack(side="right", padx=(0, 5))
                ctk.CTkButton(line, text="+", width=36, height=34, fg_color="#F4E9EE", hover_color="#E9D6DD", text_color="#713D54", command=lambda pid=product_id: change_qty(pid, 1)).pack(side="right", padx=5)
            if not cart:
                ctk.CTkLabel(cart_frame, text="Todavía no agregaste productos.", font=("Arial", 14), text_color="#51454D").pack(pady=22)
            total_label.configure(text=f"Total: $ {total:,.0f}".replace(",", "."))

        def change_qty(product_id, delta):
            item = cart.get(product_id)
            if not item: return
            item["qty"] += delta
            if item["qty"] <= 0: cart.pop(product_id)
            refresh_cart()

        def add_product(product):
            current = cart.get(product["id"], {}).get("qty", 0)
            if current >= product["stock"]:
                status.configure(text=f"No hay más unidades disponibles de {product['nombre']}.")
                return
            if product["id"] not in cart:
                cart[product["id"]] = {"name": product["nombre"], "price": float(product["precio_venta"]), "qty": 0}
            cart[product["id"]]["qty"] += 1
            status.configure(text="")
            refresh_cart()

        def search_products(_event=None):
            for child in results.winfo_children(): child.destroy()
            term = search.get().strip()
            if len(term) < 1: return
            with conectar_db() as conn:
                products = conn.execute("SELECT id,nombre,categoria,stock,precio_venta FROM productos WHERE precio_venta>0 AND nombre LIKE ? ORDER BY nombre COLLATE NOCASE LIMIT 12", (f"%{term}%",)).fetchall()
            for product in products:
                text = f"{product['nombre']} · {product['stock']} disponibles · $ {product['precio_venta']:,.0f}".replace(",", ".")
                button = ctk.CTkButton(results, text=text, anchor="w", height=38, fg_color="transparent", hover_color="#EBD5DE", text_color="#30232B", font=("Arial", 13), state="normal" if product["stock"] else "disabled", command=lambda p=product: add_product(p))
                button.pack(fill="x", padx=4, pady=2)
            if not products:
                ctk.CTkLabel(results, text="No encontramos productos disponibles con ese nombre.", text_color="#51454D", font=("Arial", 13)).pack(pady=12)

        search.bind("<KeyRelease>", search_products)
        ctk.CTkButton(footer, text="Confirmar venta", width=150, height=44, fg_color="#3F7458", hover_color="#315D46", text_color="white", font=("Arial", 14, "bold"), command=lambda: finish_sale()).pack(side="right")
        def finish_sale():
            if not cart:
                status.configure(text="Agregá al menos un producto antes de confirmar.")
                return
            try:
                with conectar_db() as conn:
                    sale_id, total = registrar_venta_local(conn, [(pid, item["qty"]) for pid, item in cart.items()], method.get())
            except ValueError as error:
                status.configure(text=str(error))
                return
            except sqlite3.Error as error:
                messagebox.showerror("No se pudo registrar la venta", str(error), parent=dialog)
                return
            dialog.destroy()
            self.cargar_pedidos()
            messagebox.showinfo("Venta registrada", f"Venta local #{sale_id} · Total $ {total:,.0f}".replace(",", "."), parent=self)

        refresh_cart()
        search.focus_set()

    def historial_local(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Historial de ventas locales")
        dialog.geometry("690x560")
        dialog.transient(self.winfo_toplevel())
        ctk.CTkLabel(dialog, text="Ventas locales recientes", font=("Arial", 21, "bold"), text_color="#30232B").pack(anchor="w", padx=20, pady=(18, 10))
        rows = ctk.CTkScrollableFrame(dialog, fg_color="white")
        rows.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        with conectar_db() as conn:
            sales = conn.execute("SELECT id,fecha,total,metodo_pago,estado FROM ventas ORDER BY id DESC LIMIT 100").fetchall()
            for sale in sales:
                items = conn.execute("SELECT nombre_producto,cantidad,precio_unitario FROM venta_items WHERE venta_id=? ORDER BY id", (sale["id"],)).fetchall()
                detail = "\n".join(f"{item['cantidad']} × {item['nombre_producto']} · $ {item['precio_unitario']:,.0f}".replace(",", ".") for item in items) or "Venta anterior sin detalle de artículos"
                card = ctk.CTkFrame(rows, fg_color="#FFFCFB", corner_radius=8)
                card.pack(fill="x", pady=5, padx=3)
                ctk.CTkLabel(card, text=f"Venta local #{sale['id']} · {sale['fecha']} · {sale['metodo_pago'] or 'Sin método'} · {sale['estado']}", font=("Arial", 14, "bold"), text_color="#30232B").pack(anchor="w", padx=12, pady=(10, 3))
                ctk.CTkLabel(card, text=detail, justify="left", anchor="w", font=("Arial", 13), text_color="#51454D").pack(anchor="w", padx=12)
                ctk.CTkLabel(card, text=f"Total: $ {sale['total']:,.0f}".replace(",", "."), font=("Arial", 14, "bold"), text_color="#713D54").pack(anchor="w", padx=12, pady=(4, 10))
                if sale["estado"] == "Registrada" and items:
                    ctk.CTkButton(card, text="Anular y reponer stock", height=38, fg_color="#F7E9E8", hover_color="#EED7D5", text_color="#713D54", font=("Arial", 13), command=lambda sid=sale["id"], parent=dialog: self.anular_venta(sid, parent)).pack(anchor="e", padx=12, pady=(0, 10))
        if not sales:
            ctk.CTkLabel(rows, text="Todavía no hay ventas locales registradas.", font=("Arial", 14), text_color="#51454D").pack(pady=24)

    def anular_venta(self, sale_id, dialog):
        if not messagebox.askyesno("Anular venta local", f"¿Anular la venta #{sale_id} y devolver sus unidades al inventario? Esta acción se registra en el historial.", parent=dialog):
            return
        try:
            with conectar_db() as conn:
                anulada = anular_venta_local(conn, sale_id)
        except (sqlite3.Error, ValueError) as error:
            messagebox.showerror("No se pudo anular", str(error), parent=dialog)
            return
        if not anulada:
            messagebox.showinfo("Venta sin cambios", "La venta ya fue anulada o no tiene detalle de productos para reponer.", parent=dialog)
            return
        dialog.destroy()
        self.historial_local()
