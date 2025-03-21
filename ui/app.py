#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Clase principal de la aplicación
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import webbrowser

from config import SPOTIFY_BLACK
from ui.splash_screen import SplashScreen
from ui.main_screen import MainScreen
from ui.styles import setup_styles

class ListifyApp:
    """Clase principal de la aplicación"""
    def __init__(self, root):
        self.root = root
        self.root.title("Listify")
        self.root.geometry("850x850")
        self.root.configure(bg=SPOTIFY_BLACK)
        self.root.minsize(850, 850)
        
        # Configurar icono de la aplicación
        self._setup_icon()
        
        # Variables compartidas
        self.shared_vars = {
            'destino_var': tk.StringVar(value="No seleccionado"),
            'current_task': tk.StringVar(value=""),
            'progress_var': tk.DoubleVar(value=0.0),
            'playlist_title': tk.StringVar(value=""),
            'status_text': tk.StringVar(value="Listo para descargar")
        }
        
        # Crear frames principales
        self.splash_screen = SplashScreen(self.root, self._abrir_inicio, self._abrir_redes)
        self.main_screen = MainScreen(self.root, self.shared_vars, self._volver_inicio, self._abrir_redes, self._seleccionar_destino)
        
        # Configurar estilos
        setup_styles(self.main_screen, self.splash_screen)
        
        # Iniciar con la pantalla de inicio
        self.mostrar_splash()

    def _setup_icon(self):
        """Configura el icono de la aplicación"""
        try:
            from PIL import Image, ImageTk
            import requests
            from io import BytesIO
            
            icon = Image.open(BytesIO(requests.get("https://www.freepnglogos.com/uploads/spotify-logo-png/file-spotify-logo-png-4.png").content))
            photo = ImageTk.PhotoImage(icon)
            self.root.iconphoto(False, photo)
        except Exception:
            pass
    
    def mostrar_splash(self):
        """Muestra la pantalla de inicio"""
        self.splash_screen.frame.pack(fill=tk.BOTH, expand=True)
        self.main_screen.frame.pack_forget()
    
    def _abrir_inicio(self):
        """Abre la pantalla principal"""
        self.splash_screen.frame.pack_forget()
        self.main_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _volver_inicio(self):
        """Vuelve a la pantalla de inicio"""
        self.main_screen.frame.pack_forget()
        self.splash_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _abrir_redes(self):
        """Abre el enlace a redes sociales"""
        webbrowser.open("https://www.instagram.com/stef.dev_/")
    
    def _seleccionar_destino(self):
        """Abre el diálogo para seleccionar carpeta destino"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.shared_vars['destino_var'].set(folder_selected)