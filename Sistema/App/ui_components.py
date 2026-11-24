"""Componentes de interfaz con limpieza compatible con CustomTkinter 5.2.x."""
import tkinter

import customtkinter as ctk
from customtkinter.windows.widgets.scaling.scaling_tracker import ScalingTracker


class SafeOptionMenu(ctk.CTkOptionMenu):
    """CTk 5.2.x no desregistra el menú interno al destruir un OptionMenu."""

    def destroy(self):
        menu = getattr(self, "_dropdown_menu", None)
        if menu is not None:
            # DropdownMenu.destroy() en CTk 5.2.2 omite CTkScalingBaseClass.destroy().
            ScalingTracker.remove_widget(menu._set_scaling, menu)
            try:
                if menu.winfo_exists():
                    menu.destroy()
            except tkinter.TclError:
                pass
        super().destroy()
