#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Clase principal de la aplicación refactorizada
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import webbrowser
import os
import sys

from config import SPOTIFY_BLACK, SPOTIFY_GREEN, SPOTIFY_DARK_GRAY
from ui.splash_screen import SplashScreen
from ui.main_screen import MainScreen
from ui.about_screen import AboutScreen  # Nueva pantalla para Acerca de
from ui.player_screen import PlayerScreen  # Nueva pantalla para el reproductor
from ui.styles import setup_styles

class ListifyApp:
    """Clase principal de la aplicación con soporte para pantalla completa"""
    def __init__(self, root):
        self.root = root
        self.root.title("Listify")
        
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Establecer tamaño inicial al 100% de la pantalla (pantalla completa sin -fullscreen)
        window_width = screen_width
        window_height = screen_height
        
        # Centrar la ventana
        x_pos = 0
        y_pos = 0
        
        # Configurar geometría
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.root.configure(bg=SPOTIFY_BLACK)
        self.root.minsize(900, 700)
        
        # Iniciar en modo pantalla completa
        self.root.attributes("-fullscreen", True)
        
        # Configurar icono de la aplicación
        self._setup_icon()
        
        # Variables compartidas
        self.shared_vars = {
            'destino_var': tk.StringVar(value="No seleccionado"),
            'current_task': tk.StringVar(value=""),
            'progress_var': tk.DoubleVar(value=0.0),
            'playlist_title': tk.StringVar(value=""),
            'status_text': tk.StringVar(value="Listo para descargar"),
            'is_fullscreen': tk.BooleanVar(value=True)  # Iniciar como True
        }
        
        # Crear frames principales
        self.splash_screen = SplashScreen(self.root, self._abrir_inicio, self._abrir_redes)
        self.main_screen = MainScreen(
            self.root, 
            self.shared_vars, 
            self._volver_inicio, 
            self._abrir_redes, 
            self._seleccionar_destino,
            self._abrir_acerca_de,
            self._toggle_fullscreen,
            self._abrir_reproductor  # Añadir callback del reproductor
        )
        self.about_screen = AboutScreen(self.root, self._volver_main)
        self.player_screen = PlayerScreen(self.root, self.shared_vars, self._volver_main)
        
        # Configurar estilos
        setup_styles(self.main_screen, self.splash_screen)
        
        # Configurar acceso rápido para pantalla completa
        self.root.bind("<F11>", lambda event: self._toggle_fullscreen())
        self.root.bind("<Escape>", lambda event: self._exit_fullscreen())
        
        # Iniciar con la pantalla de inicio
        self.mostrar_splash()

    def _setup_icon(self):
        """Configura el icono de la aplicación"""
        try:
            from PIL import Image, ImageTk
            import requests
            from io import BytesIO
            
            # Intentar cargar desde URL
            try:
                icon = Image.open(BytesIO(requests.get(
                    "https://www.freepnglogos.com/uploads/spotify-logo-png/file-spotify-logo-png-4.png"
                ).content))
                photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(False, photo)
            except:
                # Alternativa: buscar ícono local
                icon_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icon.png"),
                    os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "assets", "icon.png")
                ]
                
                for path in icon_paths:
                    if os.path.exists(path):
                        icon = Image.open(path)
                        photo = ImageTk.PhotoImage(icon)
                        self.root.iconphoto(False, photo)
                        break
        except Exception as e:
            print(f"Error al cargar el icono: {e}")
    
    def mostrar_splash(self):
        """Muestra la pantalla de inicio"""
        self.splash_screen.frame.pack(fill=tk.BOTH, expand=True)
        self.main_screen.frame.pack_forget()
        self.about_screen.frame.pack_forget()
        self.player_screen.frame.pack_forget()
    
    def _abrir_inicio(self):
        """Abre la pantalla principal"""
        self.splash_screen.frame.pack_forget()
        self.about_screen.frame.pack_forget()
        self.player_screen.frame.pack_forget()
        self.main_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _volver_inicio(self):
        """Vuelve a la pantalla de inicio"""
        self.main_screen.frame.pack_forget()
        self.about_screen.frame.pack_forget()
        self.player_screen.frame.pack_forget()
        self.splash_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _volver_main(self):
        """Vuelve a la pantalla principal desde otras pantallas"""
        self.splash_screen.frame.pack_forget()
        self.about_screen.frame.pack_forget()
        self.player_screen.frame.pack_forget()
        self.main_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _abrir_acerca_de(self):
        """Abre la pantalla de Acerca de"""
        self.splash_screen.frame.pack_forget()
        self.main_screen.frame.pack_forget()
        self.player_screen.frame.pack_forget()
        self.about_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _abrir_reproductor(self):
        """Abre la pantalla del reproductor de música"""
        self.splash_screen.frame.pack_forget()
        self.main_screen.frame.pack_forget()
        self.about_screen.frame.pack_forget()
        self.player_screen.frame.pack(fill=tk.BOTH, expand=True)
    
    def _abrir_redes(self, network="instagram"):
        """Abre enlaces a redes sociales"""
        social_links = {
            "instagram": "https://www.instagram.com/stef.dev_/",
            "github": "https://github.com/stefdev_",
            "twitter": "https://twitter.com/stefdev_",
            "linkedin": "https://linkedin.com/in/stefdev"
        }
        
        link = social_links.get(network.lower(), social_links["instagram"])
        webbrowser.open(link)
    
    def _seleccionar_destino(self):
        """Abre el diálogo para seleccionar carpeta destino"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.shared_vars['destino_var'].set(folder_selected)
    
    def _toggle_fullscreen(self):
        """Alterna el modo de pantalla completa"""
        is_full = not self.shared_vars['is_fullscreen'].get()
        self.shared_vars['is_fullscreen'].set(is_full)
        self.root.attributes("-fullscreen", is_full)
        
        # Actualizar botón en la interfaz si existe
        if hasattr(self.main_screen, 'update_fullscreen_button'):
            self.main_screen.update_fullscreen_button(is_full)
    
    def _exit_fullscreen(self):
        """Sale del modo de pantalla completa"""
        if self.shared_vars['is_fullscreen'].get():
            self.shared_vars['is_fullscreen'].set(False)
            self.root.attributes("-fullscreen", False)
            
            # Actualizar botón en la interfaz si existe
            if hasattr(self.main_screen, 'update_fullscreen_button'):
                self.main_screen.update_fullscreen_button(False)