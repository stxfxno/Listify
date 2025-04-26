#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Pantalla Acerca de
"""
import tkinter as tk
import webbrowser
from config import SPOTIFY_BLACK, SPOTIFY_GREEN, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY

class AboutScreen:
    """Clase para la pantalla de información 'Acerca de'"""
    def __init__(self, parent, volver_callback):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=SPOTIFY_BLACK)
        self.volver_callback = volver_callback
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear los widgets de la pantalla de información"""
        # Header con botón de volver
        self.header_frame = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="Acerca de Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 18, "bold")
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        self.back_btn = tk.Button(
            self.header_frame, 
            text="Volver", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.volver_callback
        )
        self.back_btn.pack(side=tk.RIGHT, padx=10)
        
        # Contenedor principal centrado
        self.main_container = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo grande
        self.logo_label = tk.Label(
            self.main_container, 
            text="🎵 Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 36, "bold")
        )
        self.logo_label.pack(pady=(0, 20))
        
        # Versión
        self.version_label = tk.Label(
            self.main_container, 
            text="Versión 1.2.0", 
            fg=SPOTIFY_LIGHT_GRAY, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 12)
        )
        self.version_label.pack(pady=(0, 30))
        
        # Descripción
        self.desc_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.desc_frame.pack(pady=10, fill=tk.X)
        
        self.desc_label = tk.Label(
            self.desc_frame,
            text="Listify es una aplicación para descargar música de Spotify a través de YouTube.\n"
                "Nació como una herramienta para preparar listas de reproducción para fiestas familiares\n"
                "sin necesidad de tener conexión a internet.",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            justify=tk.CENTER,
            wraplength=500
        )
        self.desc_label.pack()
        
        # Desarrollador
        self.dev_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.dev_frame.pack(pady=30, fill=tk.X)
        
        self.dev_title = tk.Label(
            self.dev_frame,
            text="Desarrollado por:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10)
        )
        self.dev_title.pack()
        
        self.dev_name = tk.Label(
            self.dev_frame,
            text="Stef.dev",
            fg=SPOTIFY_GREEN,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 14, "bold"),
            cursor="hand2"
        )
        self.dev_name.pack(pady=5)
        self.dev_name.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/stef.dev_/"))
        
        # Tecnologías usadas
        self.tech_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.tech_frame.pack(pady=20, fill=tk.X)
        
        self.tech_title = tk.Label(
            self.tech_frame,
            text="Tecnologías utilizadas:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10)
        )
        self.tech_title.pack()
        
        self.tech_list = tk.Label(
            self.tech_frame,
            text="Python • Tkinter • Spotipy • yt-dlp • Mutagen",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10)
        )
        self.tech_list.pack(pady=5)
        
        # Agradecimientos
        self.thanks_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.thanks_frame.pack(pady=20, fill=tk.X)
        
        self.thanks_label = tk.Label(
            self.thanks_frame,
            text="Gracias por usar Listify ❤️",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 12, "italic")
        )
        self.thanks_label.pack()
        
        # Botones de redes sociales
        self.social_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.social_frame.pack(pady=20)
        
        # Crear botones sociales
        social_networks = [
            ("Instagram", "https://www.instagram.com/stef.dev_/"),
            ("GitHub", "https://github.com/stefdev_"),
            ("Twitter", "https://twitter.com/stefdev_"),
            ("LinkedIn", "https://linkedin.com/in/stefdev")
        ]
        
        for name, url in social_networks:
            btn = tk.Button(
                self.social_frame,
                text=name,
                font=("Helvetica", 10),
                bg=SPOTIFY_DARK_GRAY,
                fg="white",
                padx=10,
                pady=5,
                borderwidth=0,
                command=lambda u=url: webbrowser.open(u)
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Agregar efectos hover
            btn.bind("<Enter>", self._on_enter)
            btn.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Efecto al pasar el mouse sobre un botón"""
        event.widget.config(bg="#444444", cursor="hand2")
    
    def _on_leave(self, event):
        """Efecto al quitar el mouse de un botón"""
        event.widget.config(bg=SPOTIFY_DARK_GRAY)