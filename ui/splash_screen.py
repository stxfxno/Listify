#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Pantalla de inicio
"""
import tkinter as tk
from config import SPOTIFY_BLACK, SPOTIFY_GREEN, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY

class SplashScreen:
    """Clase para la pantalla de inicio de la aplicación"""
    def __init__(self, parent, inicio_callback, redes_callback):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=SPOTIFY_BLACK)
        
        # Callbacks
        self.inicio_callback = inicio_callback
        self.redes_callback = redes_callback
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear los widgets de la pantalla de inicio"""
        # Contenedor principal
        self.main_container = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo grande
        self.logo_label = tk.Label(
            self.main_container, 
            text="🎵 Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 48, "bold")
        )
        self.logo_label.pack(pady=(0, 20))
        
        # Eslogan
        self.slogan_label = tk.Label(
            self.main_container, 
            text="Tu música favorita, donde quieras", 
            fg=SPOTIFY_LIGHT_GRAY, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 16)
        )
        self.slogan_label.pack(pady=(0, 40))
        
        # Botones estilizados
        self.buttons_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.buttons_frame.pack(pady=(0, 50))
        
        self.inicio_btn = tk.Button(
            self.buttons_frame, 
            text="COMENZAR", 
            font=("Helvetica", 12, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=20, 
            pady=10,
            borderwidth=0,
            command=self.inicio_callback
        )
        self.inicio_btn.pack(side=tk.LEFT, padx=10)
        
        self.redes_btn = tk.Button(
            self.buttons_frame, 
            text="CONTACTO", 
            font=("Helvetica", 12),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=20, 
            pady=10,
            borderwidth=0,
            command=self.redes_callback
        )
        self.redes_btn.pack(side=tk.LEFT, padx=10)
        
        # Footer
        self.footer_label = tk.Label(
            self.frame, 
            text="Desarrollado por stef.dev_", 
            fg=SPOTIFY_LIGHT_GRAY, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 10)
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=20)