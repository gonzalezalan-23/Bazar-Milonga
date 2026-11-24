import sqlite3
import customtkinter as ctk

from database import conectar_db


class VistaAvisos(ctk.CTkFrame):
    UMBRAL_STOCK_BAJO = 3

    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent")
        ctk.CTkLabel(self,text="Avisos de inventario",font=("Arial",27,"bold"),text_color="#30232B").pack(anchor="w",pady=(0,4))
        ctk.CTkLabel(self,text=f"Regla actual: agotado = 0 unidades · stock bajo = 1–{self.UMBRAL_STOCK_BAJO} unidades.",font=("Arial",13),text_color="#51454D",wraplength=700,justify="left").pack(anchor="w",pady=(0,16))
        self.kpi_frame=ctk.CTkFrame(self,fg_color="transparent");self.kpi_frame.pack(fill="x",pady=(0,18))
        self.main_card=ctk.CTkFrame(self,fg_color="white",corner_radius=15);self.main_card.pack(fill="both",expand=True,padx=2)
        ctk.CTkLabel(self.main_card,text="Productos para revisar",font=("Arial",18,"bold"),text_color="#713D54").pack(anchor="w",padx=24,pady=18)
        self.scroll_avisos=ctk.CTkScrollableFrame(self.main_card,fg_color="transparent");self.scroll_avisos.pack(fill="both",expand=True,padx=15,pady=(0,15))
        self.cargar_avisos()

    def cargar_avisos(self):
        for widget in self.kpi_frame.winfo_children()+self.scroll_avisos.winfo_children():widget.destroy()
        try:
            with conectar_db() as conn:productos=conn.execute("SELECT nombre,stock FROM productos WHERE stock<=? ORDER BY stock,nombre COLLATE NOCASE",(self.UMBRAL_STOCK_BAJO,)).fetchall()
        except sqlite3.Error as error:
            ctk.CTkLabel(self.scroll_avisos,text=f"No se pudieron leer las alertas: {error}",text_color="#8B344D",wraplength=600).pack(pady=30);return
        agotados=sum(producto["stock"]==0 for producto in productos);bajos=len(productos)-agotados
        self.crear_kpi("Agotados",str(agotados),0,"#FCE9EC")
        self.crear_kpi(f"Stock bajo (1–{self.UMBRAL_STOCK_BAJO})",str(bajos),1,"#FFF5D9")
        self.crear_kpi("Productos a revisar",str(len(productos)),2,"#F4E9EE")
        if not productos:
            ctk.CTkLabel(self.scroll_avisos,text="No hay productos por debajo del umbral. El inventario está al día.",text_color="#51454D",font=("Arial",14),wraplength=600,justify="center").pack(pady=40);return
        for producto in productos:
            if producto["stock"]==0:mensaje="Agotado: no hay unidades disponibles para reservar.";tipo="critico"
            else:mensaje=f"Quedan {producto['stock']} unidades. Revisá si hace falta reponer.";tipo="advertencia"
            self.agregar_aviso(producto["nombre"],mensaje,tipo)

    def crear_kpi(self,titulo,valor,col,color_fondo):
        card=ctk.CTkFrame(self.kpi_frame,fg_color=color_fondo,corner_radius=12,height=104);card.grid(row=0,column=col,padx=(0,12),sticky="nsew");self.kpi_frame.grid_columnconfigure(col,weight=1)
        ctk.CTkLabel(card,text=titulo,font=("Arial",13,"bold"),text_color="#51454D").pack(pady=(15,0))
        ctk.CTkLabel(card,text=valor,font=("Arial",25,"bold"),text_color="#30232B").pack(pady=(0,14))

    def agregar_aviso(self,producto,mensaje,tipo):
        critico=tipo=="critico";borde="#9B3D52" if critico else "#946000";fondo="#FCE9EC" if critico else "#FFF5D9";estado="AGOTADO" if critico else "STOCK BAJO"
        fila=ctk.CTkFrame(self.scroll_avisos,fg_color=fondo,corner_radius=9,border_width=1,border_color=borde);fila.pack(fill="x",pady=5,padx=5)
        content=ctk.CTkFrame(fila,fg_color="transparent");content.pack(fill="x",padx=16,pady=12)
        top=ctk.CTkFrame(content,fg_color="transparent");top.pack(fill="x")
        ctk.CTkLabel(top,text=producto,font=("Arial",14,"bold"),text_color="#30232B",anchor="w",wraplength=480).pack(side="left",fill="x",expand=True)
        ctk.CTkLabel(top,text=estado,font=("Arial",11,"bold"),text_color=borde).pack(side="right",padx=(8,0))
        ctk.CTkLabel(content,text=mensaje,font=("Arial",13),text_color="#51454D",anchor="w",wraplength=620,justify="left").pack(anchor="w",pady=(4,0))
