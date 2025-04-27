#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Pantalla principal rediseñada según el nuevo layout
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser

from config import SPOTIFY_BLACK, SPOTIFY_GREEN, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY
from services.spotify_service import search_spotify, get_tracks_from_url
from services.youtube_service import download_tracks
from services.metadata_service import get_basic_metadata

class MainScreen:
    """Clase para la pantalla principal de la aplicación con nuevo layout"""
    def __init__(self, parent, shared_vars, volver_callback, redes_callback, 
                 destino_callback, acerca_callback, fullscreen_callback, reproductor_callback=None):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=SPOTIFY_BLACK)
        
        # Variables compartidas
        self.shared_vars = shared_vars
        
        # Variables adicionales para metadatos
        self.current_cover_url = None
        self.current_album_name = None
        
        # Callbacks
        self.volver_callback = volver_callback
        self.redes_callback = redes_callback
        self.destino_callback = destino_callback
        self.acerca_callback = acerca_callback
        self.fullscreen_callback = fullscreen_callback
        self.reproductor_callback = reproductor_callback
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear los widgets según el nuevo layout"""
        # Frame principal que contiene todo
        self.content_frame = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ===== SECCIÓN SUPERIOR =====
        # Header con logo a la izquierda y botones a la derecha
        self._create_header()
        
        # Crear un frame contenedor para dividir la pantalla en dos secciones
        self.main_container = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.main_container.pack(fill=tk.BOTH, expand=True)
    
        
        # ===== SECCIÓN DE BÚSQUEDA (PARTE IZQUIERDA) =====
        # Crear un frame contenedor con capacidad de scroll
        self.left_container = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Sección izquierda con tamaño fijo
        self.left_section = tk.Frame(self.left_container, bg=SPOTIFY_BLACK, width=650)
        self.left_section.pack(fill=tk.BOTH, expand=True)
        self.left_section.pack_propagate(False)  # Mantener el ancho fijo
        
        # Campos de búsqueda
        self._create_search_controls()
        
        # Sección de información y portada
        self._create_info_section()
        
        # Crear un frame para rellenar el espacio y empujar la sección de descarga hacia abajo
        self.push_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.push_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sección de descarga y progreso al final
        self._create_download_section()
        
        # ===== SECCIÓN DE RESULTADOS (PARTE DERECHA) =====
        # Aumentar el ancho relativo de la sección derecha (60%)
        self.right_section = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.right_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Lista de canciones
        self._create_results_section()
        
        # ===== FOOTER =====
        self._create_footer()

    def _create_header(self):
        """Crear el header con el logo a la izquierda y navegación a la derecha"""
        self.header_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo grande en verde a la izquierda
        self.logo_label = tk.Label(
            self.header_frame, 
            text="Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 24, "bold")
        )
        self.logo_label.pack(side=tk.LEFT)
        
        # Frame para los botones de navegación a la derecha
        self.nav_buttons = tk.Frame(self.header_frame, bg=SPOTIFY_BLACK)
        self.nav_buttons.pack(side=tk.RIGHT)
        
        # Botones de navegación
        buttons_config = [
            {"text": "Reproductor", "command": self.reproductor_callback},
            {"text": "Acerca de", "command": self.acerca_callback},
            {"text": "Contacto", "command": self.redes_callback},
            {"text": "Pantalla Completa", "command": self.fullscreen_callback}
        ]
        
        for config in buttons_config:
            # Solo añadir el botón de reproductor si el callback está definido
            if config["text"] == "Reproductor" and not self.reproductor_callback:
                continue
                
            btn = tk.Button(
                self.nav_buttons, 
                text=config["text"], 
                font=("Helvetica", 10),
                bg=SPOTIFY_DARK_GRAY, 
                fg="white", 
                padx=10, 
                pady=4,
                borderwidth=0,
                command=config["command"]
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Agregar efectos hover
            btn.bind("<Enter>", self._on_enter)
            btn.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        """Efecto al pasar el mouse sobre un botón"""
        e.widget.config(bg="#444444", cursor="hand2")
    
    def _on_leave(self, e):
        """Efecto al quitar el mouse de un botón"""
        e.widget.config(bg=SPOTIFY_DARK_GRAY)
    
    def update_fullscreen_button(self, is_full):
        """Actualiza el texto del botón de pantalla completa"""
        # Actualizar el texto según el estado
        for btn in self.nav_buttons.winfo_children():
            if btn.cget("command") == self.fullscreen_callback:
                btn.config(text="Salir Pantalla Completa" if is_full else "Pantalla Completa")
                break
    
    def _create_search_controls(self):
        """Crear los controles de búsqueda según el nuevo layout"""
        # Frame para URL
        self.url_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.url_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL Label
        self.url_label = tk.Label(
            self.url_frame, 
            text="URL de la Playlist:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 11),
            anchor='w'
        )
        self.url_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame para contener entrada y botón en la misma línea
        self.url_input_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.url_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL Entry
        self.url_entry = tk.Entry(
            self.url_input_frame, 
            font=("Helvetica", 11),
            bg=SPOTIFY_DARK_GRAY,
            fg="white",
            insertbackground="white"
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botón de búsqueda URL
        self.fetch_btn = tk.Button(
            self.url_input_frame, 
            text="Buscar", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.fetch_tracks
        )
        self.fetch_btn.pack(side=tk.LEFT)
        
        # Frame para búsqueda
        self.search_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda Label
        self.search_label = tk.Label(
            self.search_frame, 
            text="Buscar en Spotify:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 11),
            anchor='w'
        )
        self.search_label.pack(side=tk.LEFT)
        
        # Frame para contener entrada, tipo y botón en la misma línea
        self.search_input_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.search_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search Entry
        self.search_entry = tk.Entry(
            self.search_input_frame, 
            font=("Helvetica", 11),
            bg=SPOTIFY_DARK_GRAY,
            fg="white",
            insertbackground="white"
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botón de búsqueda
        self.search_btn = tk.Button(
            self.search_input_frame, 
            text="Buscar", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.search_spotify
        )
        self.search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Combobox para tipo de búsqueda
        self.search_type = ttk.Combobox(
            self.search_input_frame,
            values=["Canciones", "Artistas", "Álbumes"],
            width=10,
            font=("Helvetica", 10)
        )
        self.search_type.current(0)
        self.search_type.pack(side=tk.LEFT)
    
    def _create_info_section(self):
        """Crear la sección de información según el nuevo layout"""
        # Frame para resultados
        self.results_title_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.results_title_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.results_label = tk.Label(
            self.results_title_frame, 
            text="Resultados para:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 12, "bold"),
            anchor='w'
        )
        self.results_label.pack(side=tk.LEFT)
        
        # Frame que contiene portada e información
        self.info_content_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.info_content_frame.pack(fill=tk.X, pady=10)
        
        # Portada (cuadro X)
        self.cover_frame = tk.Frame(self.info_content_frame, bg=SPOTIFY_BLACK, width=150, height=150)
        self.cover_frame.pack(side=tk.LEFT, padx=(0, 15))
        self.cover_frame.pack_propagate(False)  # Mantener el tamaño fijo
        
        self.cover_label = tk.Label(self.cover_frame, bg=SPOTIFY_BLACK)
        self.cover_label.pack(fill=tk.BOTH, expand=True)
        
        # Información detallada
        self.details_frame = tk.Frame(self.info_content_frame, bg=SPOTIFY_BLACK)
        self.details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Título de la canción o playlist
        self.title_label = tk.Label(
            self.details_frame,
            textvariable=self.shared_vars['playlist_title'],
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 14, "bold"),
            wraplength=300,
            justify=tk.LEFT,
            anchor='w'
        )
        self.title_label.pack(fill=tk.X, anchor='w', pady=(0, 5))
        
        # Artista
        self.artist_label = tk.Label(
            self.details_frame,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 12),
            anchor='w',
            wraplength=300,
            justify=tk.LEFT
        )
        self.artist_label.pack(fill=tk.X, anchor='w', pady=(0, 10))
        
        # Frame para dos columnas de detalles
        self.details_grid = tk.Frame(self.details_frame, bg=SPOTIFY_BLACK)
        self.details_grid.pack(fill=tk.X, anchor='w')
        
        # Primera fila: álbum y duración
        self.details_row1 = tk.Frame(self.details_grid, bg=SPOTIFY_BLACK)
        self.details_row1.pack(fill=tk.X, pady=(0, 5))
        
        # Álbum
        self.album_label_title = tk.Label(
            self.details_row1,
            text="Album:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.album_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.album_label = tk.Label(
            self.details_row1,
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.album_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Duración
        self.duration_label_title = tk.Label(
            self.details_row1,
            text="Duración:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.duration_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.duration_label = tk.Label(
            self.details_row1,
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.duration_label.pack(side=tk.LEFT)
        
        # Segunda fila: lanzamiento y popularidad
        self.details_row2 = tk.Frame(self.details_grid, bg=SPOTIFY_BLACK)
        self.details_row2.pack(fill=tk.X)
        
        # Lanzamiento
        self.release_label_title = tk.Label(
            self.details_row2,
            text="Lanzamiento:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.release_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.release_label = tk.Label(
            self.details_row2,
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.release_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Popularidad
        self.popularity_label_title = tk.Label(
            self.details_row2,
            text="Popularidad:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.popularity_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.popularity_label = tk.Label(
            self.details_row2,
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 11),
            anchor='w'
        )
        self.popularity_label.pack(side=tk.LEFT)
    
    def _create_results_section(self):
        """Crear la sección de resultados (lista de canciones)"""
        # Título para la lista de canciones
        self.list_title_label = tk.Label(
            self.right_section, 
            text="Canciones:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 11, "bold"),
            anchor='w'
        )
        self.list_title_label.pack(fill=tk.X, anchor='w', pady=(0, 5))
        
        # Frame para lista de canciones con borde gris
        self.list_frame = tk.Frame(
            self.right_section, 
            bg=SPOTIFY_BLACK, 
            highlightbackground=SPOTIFY_DARK_GRAY,
            highlightthickness=1
        )
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contenedor para lista y scrollbar
        self.list_container = tk.Frame(self.list_frame, bg=SPOTIFY_BLACK)
        self.list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.list_container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de canciones
        self.track_list = tk.Listbox(
            self.list_container, 
            font=("Helvetica", 11),
            bg=SPOTIFY_BLACK,
            fg="white",
            selectbackground=SPOTIFY_GREEN,
            activestyle='none',
            yscrollcommand=self.scrollbar.set,
            borderwidth=0,
            highlightthickness=0
        )
        self.track_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.track_list.yview)
        
        # Añadir evento de selección
        self.track_list.bind('<<ListboxSelect>>', self._on_track_select)
    
    def _create_download_section(self):
        """Crear la sección de descarga según el nuevo layout"""
        # Frame contenedor para selección de carpeta
        self.folder_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.folder_frame.pack(fill=tk.X, pady=(20, 5))
        
        # Botón seleccionar carpeta
        self.folder_btn = tk.Button(
            self.folder_frame, 
            text="Seleccionar carpeta", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.destino_callback
        )
        self.folder_btn.pack(side=tk.LEFT)
        
        # Etiqueta carpeta seleccionada
        self.folder_label = tk.Label(
            self.folder_frame,
            textvariable=self.shared_vars['destino_var'],
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.folder_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Frame para botones de descarga
        self.download_buttons_frame = tk.Frame(self.left_section, bg=SPOTIFY_BLACK)
        self.download_buttons_frame.pack(fill=tk.X, pady=(5, 5))
        
        # Botón descargar canción
        self.download_song_btn = tk.Button(
            self.download_buttons_frame, 
            text="Descargar Canción", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=15, 
            pady=5,
            borderwidth=0,
            command=self.descargar_cancion
        )
        self.download_song_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón descargar playlist
        self.download_playlist_btn = tk.Button(
            self.download_buttons_frame, 
            text="Descargar Playlist", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=15, 
            pady=5,
            borderwidth=0,
            command=self.descargar_playlist
        )
        self.download_playlist_btn.pack(side=tk.LEFT)
        
        # Estado de descarga
        self.download_status_label = tk.Label(
            self.left_section,
            textvariable=self.shared_vars['current_task'],
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.download_status_label.pack(fill=tk.X, pady=(5, 2))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            self.left_section,
            orient="horizontal",
            mode="determinate",
            variable=self.shared_vars['progress_var']
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 2))
        
        # Texto de estado
        self.status_label = tk.Label(
            self.left_section,
            textvariable=self.shared_vars['status_text'],
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.status_label.pack(fill=tk.X)
    
    def _create_footer(self):
        """Crear el pie de página según el nuevo layout"""
        self.footer = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # Copyright a la izquierda
        self.footer_left = tk.Label(
            self.footer,
            text="© 2025 Listify - V1.3.0",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9)
        )
        self.footer_left.pack(side=tk.LEFT)
        
        # Redes sociales a la derecha
        self.footer_right = tk.Frame(self.footer, bg=SPOTIFY_BLACK)
        self.footer_right.pack(side=tk.RIGHT)
        
        # Función para crear botones sociales más compactos
        def create_social_button(text, network):
            btn = tk.Button(
                self.footer_right,
                text=text,
                font=("Helvetica", 8),
                bg=SPOTIFY_BLACK,
                fg=SPOTIFY_LIGHT_GRAY,
                borderwidth=0,
                padx=2,
                pady=0,
                command=lambda: self.redes_callback(network)
            )
            btn.pack(side=tk.LEFT, padx=1)
            return btn
        
        # Crear botones para diferentes redes
        self.instagram_btn = create_social_button("Instagram", "instagram")
        self.github_btn = create_social_button("GitHub", "github")
        self.twitter_btn = create_social_button("Twitter", "twitter")
        self.linkedin_btn = create_social_button("LinkedIn", "linkedin")
    
    # ===== MÉTODOS FUNCIONALES =====
    
    def fetch_tracks(self):
        """Obtener pistas desde una URL de Spotify"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Advertencia", "Por favor ingresa una URL de Spotify.")
            return
        
        # Mostrar indicador de carga
        self.shared_vars['status_text'].set("Obteniendo datos de Spotify...")
        self.track_list.delete(0, tk.END)
        self.shared_vars['playlist_title'].set("")
        self.cover_label.config(image="")
        self.shared_vars['progress_var'].set(20)
        self.parent.update()
        
        # Reiniciar información de metadatos
        self.current_cover_url = None
        self.current_album_name = None
        
        # Ejecutar en un hilo separado para no congelar la UI
        threading.Thread(target=self._fetch_tracks_thread, args=(url,), daemon=True).start()
    
    def _fetch_tracks_thread(self, url):
        """Hilo para obtener pistas de Spotify"""
        tracks, cover_url, title = get_tracks_from_url(url)
        
        # Guardar información de metadatos
        self.current_cover_url = cover_url
        self.current_album_name = title
        
        # Actualizar la UI en el hilo principal
        self.parent.after(0, lambda: self._update_tracks_ui(tracks, cover_url, title))
    
    def _update_tracks_ui(self, tracks, cover_url, title):
        """Actualizar la UI con las pistas obtenidas"""
        if tracks:
            for track in tracks:
                self.track_list.insert(tk.END, track)
            
            self.shared_vars['playlist_title'].set(title)
            
            if cover_url:
                try:
                    from PIL import Image, ImageTk
                    import requests
                    from io import BytesIO
                    
                    response = requests.get(cover_url)
                    img_data = BytesIO(response.content)
                    cover_img = Image.open(img_data).resize((150, 150), Image.LANCZOS)
                    cover_photo = ImageTk.PhotoImage(cover_img)
                    self.cover_label.config(image=cover_photo)
                    self.cover_label.image = cover_photo
                except Exception as e:
                    print(f"Error al cargar la portada: {e}")
        
        self.shared_vars['progress_var'].set(100)
        self.shared_vars['status_text'].set(f"Listo - {len(tracks)} canciones encontradas")
        
        # Reiniciar la barra de progreso después de un tiempo
        self.parent.after(3000, lambda: self.shared_vars['progress_var'].set(0))
    
    def search_spotify(self):
        """Buscar en Spotify"""
        search_query = self.search_entry.get().strip()
        search_type = self.search_type.get().lower()
        
        if not search_query:
            messagebox.showwarning("Advertencia", "Por favor ingresa un término de búsqueda.")
            return
        
        # Mostrar indicador de carga
        self.shared_vars['status_text'].set(f"Buscando {search_type} en Spotify...")
        self.track_list.delete(0, tk.END)
        self.shared_vars['playlist_title'].set("")
        self.cover_label.config(image="")
        self.shared_vars['progress_var'].set(20)
        self.parent.update()
        
        # Reiniciar información de metadatos
        self.current_cover_url = None
        self.current_album_name = None
        
        # Ejecutar en un hilo separado para no congelar la UI
        threading.Thread(target=self._search_spotify_thread, 
                     args=(search_query, search_type), 
                     daemon=True).start()

    def _search_spotify_thread(self, query, search_type):
        """Hilo para buscar en Spotify"""
        results, cover_url, title = search_spotify(query, search_type)
        
        # Guardar información de metadatos
        self.current_cover_url = cover_url
        self.current_album_name = title
        
        # Actualizar la UI en el hilo principal
        self.parent.after(0, lambda: self._update_search_ui(results, cover_url, title))

    def _update_search_ui(self, results, cover_url, title):
        """Actualizar la UI con los resultados de búsqueda"""
        if results:
            for item in results:
                self.track_list.insert(tk.END, item)
            
            self.shared_vars['playlist_title'].set(title)
            
            if cover_url:
                try:
                    from PIL import Image, ImageTk
                    import requests
                    from io import BytesIO
                    
                    response = requests.get(cover_url)
                    img_data = BytesIO(response.content)
                    cover_img = Image.open(img_data).resize((150, 150), Image.LANCZOS)
                    cover_photo = ImageTk.PhotoImage(cover_img)
                    self.cover_label.config(image=cover_photo)
                    self.cover_label.image = cover_photo
                except Exception as e:
                    print(f"Error al cargar la portada: {e}")
        
        self.shared_vars['progress_var'].set(100)
        self.shared_vars['status_text'].set(f"Listo - {len(results)} resultados encontrados")
        
        # Reiniciar la barra de progreso después de un tiempo
        self.parent.after(3000, lambda: self.shared_vars['progress_var'].set(0))
    
    def descargar_cancion(self):
        """Descargar la canción seleccionada"""
        selected_song = self.track_list.get(tk.ACTIVE)
        if not selected_song:
            messagebox.showwarning("Advertencia", "Selecciona una canción para descargar.")
            return
        
        threading.Thread(target=self._descargar_audio, args=([selected_song],), daemon=True).start()
    
    def descargar_playlist(self):
        """Descargar todas las canciones de la lista"""
        if self.track_list.size() == 0:
            messagebox.showwarning("Advertencia", "No hay canciones en la lista.")
            return
        
        tracks = [self.track_list.get(i) for i in range(self.track_list.size())]
        threading.Thread(target=self._descargar_audio, args=(tracks,), daemon=True).start()
    
    def _descargar_audio(self, tracks):
        """Proceso de descarga de audio en segundo plano"""
        destino = self.shared_vars['destino_var'].get()
        if not destino or destino == "No seleccionado":
            self.parent.after(0, lambda: messagebox.showerror("Error", "Selecciona un destino primero."))
            return
        
        # Determinar si se deben incluir metadatos
        use_metadata = True  # En el nuevo diseño no hay checkbox, pero mantenemos la funcionalidad
        
        # Usar los metadatos recopilados solo si están marcados para incluirse
        cover_url = self.current_cover_url if use_metadata else None
        album_name = self.current_album_name if use_metadata else None
        
        # Descargar las pistas
        download_tracks(tracks, destino, self.parent, self.shared_vars, cover_url, album_name)
    
    def _on_track_select(self, event):
        """Actualiza los detalles de la canción cuando se selecciona una pista"""
        if not self.track_list.curselection():
            return
        
        selected_index = self.track_list.curselection()[0]
        track_name = self.track_list.get(selected_index)
        
        # Ignorar categorías o separadores (líneas que comienzan con espacios o contienen ÁLBUM:)
        if track_name.strip().startswith("•") or "ÁLBUM:" in track_name:
            return
        
        # Mostrar indicador de carga
        self.shared_vars['status_text'].set("Cargando detalles de la canción...")
        
        # Ejecutar en un hilo separado
        threading.Thread(target=self._fetch_track_details, args=(track_name,), daemon=True).start()

    def _fetch_track_details(self, track_name):
        """Obtiene los detalles de una canción en segundo plano"""
        from services.spotify_service import get_track_details
        
        details = get_track_details(track_name)
        
        # Actualizar la UI en el hilo principal
        self.parent.after(0, lambda: self._update_track_details_ui(track_name, details))

    def _update_track_details_ui(self, track_name, details):
        """Actualiza la interfaz con los detalles de la canción"""
        # Reiniciar estado
        self.shared_vars['status_text'].set("Listo")
        
        if not details:
            # Mostrar información básica si no hay detalles disponibles
            parts = track_name.split(" - ", 1)
            title = parts[0].strip()
            artist = parts[1].strip() if len(parts) > 1 else "Desconocido"
            
            self.shared_vars['playlist_title'].set(title)
            self.artist_label.config(text=artist)
            self.album_label.config(text="N/A")
            self.release_label.config(text="N/A")
            self.duration_label.config(text="N/A")
            self.popularity_label.config(text="N/A")
        else:
            # Actualizar todos los campos
            self.shared_vars['playlist_title'].set(details['name'])
            self.artist_label.config(text=", ".join(details['artists']))
            self.album_label.config(text=details['album']['name'])
            self.release_label.config(text=details['album']['release_date'])
            self.duration_label.config(text=details['duration'])
            self.popularity_label.config(text=f"{details['popularity']}/100")
            
            # Actualizar portada si hay imágenes disponibles
            if details['album']['images']:
                try:
                    from PIL import Image, ImageTk
                    import requests
                    from io import BytesIO
                    
                    # Usar la primera imagen (generalmente la de mayor resolución)
                    cover_url = details['album']['images'][0]
                    
                    response = requests.get(cover_url)
                    img_data = BytesIO(response.content)
                    cover_img = Image.open(img_data).resize((150, 150), Image.LANCZOS)
                    cover_photo = ImageTk.PhotoImage(cover_img)
                    self.cover_label.config(image=cover_photo)
                    self.cover_label.image = cover_photo  # Mantener referencia
                except Exception as e:
                    print(f"Error al cargar la portada: {e}")