import json
from pathlib import Path

import customtkinter as ctk

from database import conectar_db, crear_tablas
from vista_avisos import VistaAvisos
from vista_balance import VistaBalance
from vista_ingresos import VistaIngresos
from vista_stock import VistaStock
from vista_ventas import VistaVentas

PREFERENCIAS = Path(__file__).resolve().with_name("preferencias.json")


class AppMilonga(ctk.CTk):
    def __init__(self):
        crear_tablas()
        ctk.set_appearance_mode("light")
        super().__init__()
        self.escala_interfaz = self.leer_escala()
        ctk.set_widget_scaling(self.escala_interfaz)
        self.title("Milonga - Gestión de Inventario")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        initial_width = min(1180 if self.escala_interfaz >= 1.2 else 1120, max(760, screen_width - 80))
        initial_height = min(780 if self.escala_interfaz >= 1.2 else 740, max(560, screen_height - 100))
        self.geometry(f"{initial_width}x{initial_height}")
        self.minsize(min(760, screen_width), min(560, screen_height))
        self.configure(fg_color="#FCF8F9")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color="#F8EDF1", border_width=1, border_color="#D9CBD1")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar, text="Milonga\nGestión del bazar", justify="left", font=("Arial", 20, "bold"), text_color="#713D54").pack(anchor="w", padx=20, pady=(30, 24))

        self.botones_menu = {}
        self.botones_menu["stock"] = self.crear_boton_menu("Stock actual", "stock")
        self.botones_menu["avisos"] = self.crear_boton_menu("Avisos", "avisos")
        self.botones_menu["ingresos"] = self.crear_boton_menu("Ingresos", "ingresos")
        self.botones_menu["ventas"] = self.crear_boton_menu("Ventas", "ventas")
        self.botones_menu["balance"] = self.crear_boton_menu("Balance", "balance")
        accesibilidad = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        accesibilidad.pack(side="bottom", fill="x", padx=14, pady=16)
        ctk.CTkLabel(accesibilidad, text="Tamaño de controles", anchor="w", text_color="#51454D", font=("Arial", 12)).pack(anchor="w", padx=2, pady=(0, 6))
        controles = ctk.CTkFrame(accesibilidad, fg_color="transparent")
        controles.pack(fill="x")
        ctk.CTkButton(controles, text="A−", width=70, height=40, fg_color="#FFFFFF", hover_color="#EBD5DE", text_color="#30232B", font=("Arial", 14, "bold"), command=lambda: self.cambiar_escala(-0.1)).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(controles, text="A+", width=70, height=40, fg_color="#A64F72", hover_color="#873B5A", text_color="white", font=("Arial", 14, "bold"), command=lambda: self.cambiar_escala(0.1)).pack(side="left", expand=True, fill="x", padx=(4, 0))
        self.contenedor_vistas = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_vistas.grid(row=0, column=1, sticky="nsew", padx=28, pady=26)
        self.bind("<Configure>", self._ajustar_layout)
        self.vista_actual = None
        self.cambiar_pantalla("stock")

    def crear_boton_menu(self, texto, nombre_vista):
        btn = ctk.CTkButton(self.sidebar, text=texto, fg_color="transparent", text_color="#30232B", hover_color="#EBD5DE", anchor="w", height=50, corner_radius=8, font=("Arial", 15), command=lambda: self.cambiar_pantalla(nombre_vista))
        btn.pack(fill="x", padx=14, pady=4)
        return btn

    def actualizar_badge_ventas(self):
        try:
            with conectar_db() as conn:
                pendientes = conn.execute("SELECT COUNT(*) FROM pedidos_web WHERE estado='Pendiente de coordinación'").fetchone()[0]
            label = f"Ventas  ·  {pendientes} pendiente(s)" if pendientes else "Ventas"
        except Exception:
            label = "Ventas"
        self.botones_menu["ventas"].configure(text=label)

    def resaltar_boton(self, nombre_activo):
        for nombre, boton in self.botones_menu.items():
            if nombre == nombre_activo:
                boton.configure(fg_color="#EBD5DE", text_color="#713D54", font=("Arial", 15, "bold"))
            else:
                boton.configure(fg_color="transparent", text_color="#30232B", font=("Arial", 15))

    def cambiar_escala(self, delta):
        self.escala_interfaz = min(1.3, max(0.9, round(self.escala_interfaz + delta, 1)))
        ctk.set_widget_scaling(self.escala_interfaz)
        try:
            PREFERENCIAS.write_text(json.dumps({"escala_interfaz": self.escala_interfaz}, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _ajustar_layout(self, event):
        if event.widget is not self:
            return
        compacto = event.width < 940
        sidebar_width = 178 if compacto else 210
        if self.sidebar.winfo_width() != sidebar_width:
            self.sidebar.configure(width=sidebar_width)
        margen_x = 14 if compacto else 28
        margen_y = 14 if event.height < 680 else 26
        self.contenedor_vistas.grid_configure(padx=margen_x, pady=margen_y)

    @staticmethod
    def leer_escala():
        try:
            value = float(json.loads(PREFERENCIAS.read_text(encoding="utf-8")).get("escala_interfaz", 1.0))
            return min(1.3, max(0.9, value))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return 1.0

    def cambiar_pantalla(self, nombre):
        if self.vista_actual:
            self.vista_actual.destroy()
        self.actualizar_badge_ventas()
        self.resaltar_boton(nombre)
        vistas = {"stock": VistaStock, "avisos": VistaAvisos, "ingresos": VistaIngresos, "ventas": VistaVentas, "balance": VistaBalance}
        self.vista_actual = vistas[nombre](self.contenedor_vistas)
        self.vista_actual.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = AppMilonga()
    app.mainloop()
