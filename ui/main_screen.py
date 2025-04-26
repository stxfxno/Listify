#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Pantalla principal mejorada
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
    """Clase para la pantalla principal de la aplicación"""
    def __init__(self, parent, shared_vars, volver_callback, redes_callback, 
                 destino_callback, acerca_callback, fullscreen_callback):
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
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear los widgets de la pantalla principal"""
        # Contenedor principal con barras de desplazamiento
        self.main_container = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para permitir desplazamiento
        self.canvas = tk.Canvas(self.main_container, bg=SPOTIFY_BLACK, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        # Frame que contiene todos los widgets
        self.content_frame = tk.Frame(self.canvas, bg=SPOTIFY_BLACK)
        self.content_frame.bind("<Configure>", 
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Configurar canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Ajustar el ancho del canvas al cambiar el tamaño de la ventana
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Configurar scroll con rueda del ratón
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Header con logo y navegación
        self._create_header()
        
        # Sección de URL de Spotify
        self._create_url_section()
        
        # Sección de búsqueda
        self._create_search_section()
        
        # Sección de info y portada
        self._create_info_section()
        
        # Lista de canciones con scrollbar
        self._create_tracklist_section()
        
        # Sección de descarga
        self._create_download_section()
        
        # Barra de progreso
        self._create_progress_section()
        
        # Footer
        self._create_footer()
    
    def _on_canvas_configure(self, event):
        """Ajusta el ancho del contenido al cambiar el tamaño del canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        """Maneja el desplazamiento con la rueda del ratón"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_header(self):
        """Crear el encabezado con logo y navegación"""
        self.header_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.small_logo = tk.Label(
            self.header_frame, 
            text="🎵 Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 18, "bold")
        )
        self.small_logo.pack(side=tk.LEFT, padx=10)
        
        # Frame para los botones de navegación
        self.nav_buttons = tk.Frame(self.header_frame, bg=SPOTIFY_BLACK)
        self.nav_buttons.pack(side=tk.RIGHT)
        
        # Botón de pantalla completa
        self.fullscreen_btn = tk.Button(
            self.nav_buttons, 
            text="Pantalla Completa", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.fullscreen_callback
        )
        self.fullscreen_btn.pack(side=tk.RIGHT, padx=5)
        
        # Botón de Acerca de
        self.about_btn = tk.Button(
            self.nav_buttons, 
            text="Acerca de", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.acerca_callback
        )
        self.about_btn.pack(side=tk.RIGHT, padx=5)
        
        # Botón Volver
        self.nav_btn = tk.Button(
            self.nav_buttons, 
            text="Volver", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.volver_callback
        )
        self.nav_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_url_section(self):
        """Crear la sección de entrada de URL"""
        self.url_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.url_frame.pack(fill=tk.X, padx=40, pady=10)
        
        self.url_label = tk.Label(
            self.url_frame, 
            text="URL de Spotify:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 12)
        )
        self.url_label.pack(side=tk.LEFT, padx=5)
        
        self.url_entry = tk.Entry(
            self.url_frame, 
            width=50, 
            font=("Helvetica", 12),
            bg=SPOTIFY_DARK_GRAY,
            fg="white",
            insertbackground="white"
        )
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.fetch_btn = tk.Button(
            self.url_frame, 
            text="Buscar", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.fetch_tracks
        )
        self.fetch_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_search_section(self):
        """Crear la sección de búsqueda"""
        self.search_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.search_frame.pack(fill=tk.X, padx=40, pady=10)

        self.search_label = tk.Label(
            self.search_frame, 
            text="Buscar en Spotify:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 12)
        )
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(
            self.search_frame, 
            width=40, 
            font=("Helvetica", 12),
            bg=SPOTIFY_DARK_GRAY,
            fg="white",
            insertbackground="white"
        )
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.search_type = ttk.Combobox(
            self.search_frame,
            values=["Canciones", "Artistas", "Álbumes"],
            width=10,
            font=("Helvetica", 10)
        )
        self.search_type.current(0)
        self.search_type.pack(side=tk.LEFT, padx=5)

        self.search_btn = tk.Button(
            self.search_frame, 
            text="Buscar", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self.search_spotify
        )
        self.search_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_info_section(self):
        """Crear la sección de información y portada mejorada con mejor distribución"""
        self.info_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.info_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # Frame para la portada
        self.cover_frame = tk.Frame(self.info_frame, bg=SPOTIFY_BLACK, width=150, height=150)
        self.cover_frame.pack(side=tk.LEFT, padx=10)
        self.cover_frame.pack_propagate(False)  # Mantener el tamaño fijo
        
        self.cover_label = tk.Label(self.cover_frame, bg=SPOTIFY_BLACK)
        self.cover_label.pack(fill=tk.BOTH, expand=True)
        
        # Frame para la información del título y metadatos
        self.info_content_frame = tk.Frame(self.info_frame, bg=SPOTIFY_BLACK)
        self.info_content_frame.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True, anchor='nw')
        
        # Título de la búsqueda
        self.title_label = tk.Label(
            self.info_content_frame,
            textvariable=self.shared_vars['playlist_title'],
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 16, "bold"),
            wraplength=600,
            justify=tk.LEFT,
            anchor='w'
        )
        self.title_label.pack(fill=tk.X, pady=(0, 10), anchor='w')
        
        # Detalles de la canción seleccionada
        self.song_details_frame = tk.Frame(self.info_content_frame, bg=SPOTIFY_BLACK)
        self.song_details_frame.pack(fill=tk.X, pady=5, anchor='w')
        
        # Título de la canción
        self.song_title_label = tk.Label(
            self.song_details_frame,
            text="",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 14, "bold"),
            anchor='w'
        )
        self.song_title_label.pack(fill=tk.X, anchor='w')
        
        # Artista
        self.artist_label = tk.Label(
            self.song_details_frame,
            text="",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 12),
            anchor='w'
        )
        self.artist_label.pack(fill=tk.X, anchor='w', pady=(2, 10))
        
        # Frame para detalles en dos filas con dos columnas cada una
        self.details_grid = tk.Frame(self.song_details_frame, bg=SPOTIFY_BLACK)
        self.details_grid.pack(fill=tk.X, pady=(0, 5), anchor='w')
        
        # Primera fila
        self.details_row1 = tk.Frame(self.details_grid, bg=SPOTIFY_BLACK)
        self.details_row1.pack(fill=tk.X, pady=(0, 5))
        
        # Álbum (columna 1)
        self.album_frame = tk.Frame(self.details_row1, bg=SPOTIFY_BLACK, width=300)
        self.album_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.album_label_title = tk.Label(
            self.album_frame,
            text="Álbum:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9, "bold"),
            anchor='w'
        )
        self.album_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.album_label = tk.Label(
            self.album_frame,
            text="",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.album_label.pack(side=tk.LEFT)
        
        # Duración (columna 2)
        self.duration_frame = tk.Frame(self.details_row1, bg=SPOTIFY_BLACK, width=200)
        self.duration_frame.pack(side=tk.LEFT)
        
        self.duration_label_title = tk.Label(
            self.duration_frame,
            text="Duración:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9, "bold"),
            anchor='w'
        )
        self.duration_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.duration_label = tk.Label(
            self.duration_frame,
            text="",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.duration_label.pack(side=tk.LEFT)
        
        # Segunda fila
        self.details_row2 = tk.Frame(self.details_grid, bg=SPOTIFY_BLACK)
        self.details_row2.pack(fill=tk.X)
        
        # Lanzamiento (columna 1)
        self.release_frame = tk.Frame(self.details_row2, bg=SPOTIFY_BLACK, width=300)
        self.release_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.release_label_title = tk.Label(
            self.release_frame,
            text="Lanzamiento:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9, "bold"),
            anchor='w'
        )
        self.release_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.release_label = tk.Label(
            self.release_frame,
            text="",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.release_label.pack(side=tk.LEFT)
        
        # Popularidad (columna 2)
        self.popularity_frame = tk.Frame(self.details_row2, bg=SPOTIFY_BLACK, width=200)
        self.popularity_frame.pack(side=tk.LEFT)
        
        self.popularity_label_title = tk.Label(
            self.popularity_frame,
            text="Popularidad:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9, "bold"),
            anchor='w'
        )
        self.popularity_label_title.pack(side=tk.LEFT, padx=(0, 5))
        
        self.popularity_label = tk.Label(
            self.popularity_frame,
            text="",
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.popularity_label.pack(side=tk.LEFT)
        
        # Ocultar detalles al principio
        self.song_details_frame.pack_forget()
        
    
    def _create_tracklist_section(self):
        """Crear la sección de lista de canciones con altura optimizada"""
        self.list_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        self.list_label = tk.Label(
            self.list_frame, 
            text="Canciones:", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 12)
        )
        self.list_label.pack(anchor='w', padx=5, pady=5)
        
        self.list_container = tk.Frame(self.list_frame, bg=SPOTIFY_BLACK)
        self.list_container.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.list_container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # El valor height es clave para controlar el tamaño vertical
        # Al usar un valor fijo pero no muy grande (10-12), nos aseguramos
        # que toda la interfaz se vea sin necesidad de scroll
        self.track_list = tk.Listbox(
            self.list_container, 
            width=60, 
            height=10,  # Altura reducida para evitar scroll en la ventana principal
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY,
            fg="white",
            selectbackground=SPOTIFY_GREEN,
            activestyle='none',
            yscrollcommand=self.scrollbar.set
        )
        self.track_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.track_list.yview)
        
        # Añadir evento de selección
        self.track_list.bind('<<ListboxSelect>>', self._on_track_select)
    
    def _create_download_section(self):
        """Crear la sección de descarga"""
        self.download_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.download_frame.pack(fill=tk.X, padx=40, pady=10)
        
        self.folder_frame = tk.Frame(self.download_frame, bg=SPOTIFY_BLACK)
        self.folder_frame.pack(fill=tk.X, pady=5)
        
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
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_label = tk.Label(
            self.folder_frame,
            textvariable=self.shared_vars['destino_var'],
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.folder_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Opción para incluir metadatos
        self.metadata_var = tk.BooleanVar(value=True)
        self.metadata_check = tk.Checkbutton(
            self.folder_frame,
            text="Incluir metadatos",
            variable=self.metadata_var,
            fg="white",
            bg=SPOTIFY_BLACK,
            selectcolor=SPOTIFY_DARK_GRAY,
            activebackground=SPOTIFY_BLACK,
            activeforeground="white"
        )
        self.metadata_check.pack(side=tk.RIGHT, padx=10)
        
        # Botones de descarga
        self.buttons_download_frame = tk.Frame(self.download_frame, bg=SPOTIFY_BLACK)
        self.buttons_download_frame.pack(fill=tk.X, pady=10)
        
        self.download_song_btn = tk.Button(
            self.buttons_download_frame, 
            text="Descargar canción", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=15, 
            pady=8,
            borderwidth=0,
            command=self.descargar_cancion
        )
        self.download_song_btn.pack(side=tk.LEFT, padx=5)
        
        self.download_playlist_btn = tk.Button(
            self.buttons_download_frame, 
            text="Descargar playlist", 
            font=("Helvetica", 10, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=15, 
            pady=8,
            borderwidth=0,
            command=self.descargar_playlist
        )
        self.download_playlist_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_progress_section(self):
        """Crear la sección de progreso"""
        self.progress_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.progress_frame.pack(fill=tk.X, padx=40, pady=5)
        
        self.current_task_label = tk.Label(
            self.progress_frame,
            textvariable=self.shared_vars['current_task'],
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.current_task_label.pack(fill=tk.X, padx=5, pady=2)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            mode="determinate",
            variable=self.shared_vars['progress_var']
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = tk.Label(
            self.progress_frame,
            textvariable=self.shared_vars['status_text'],
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def _create_footer(self):
        """Crear el pie de página mejorado y compacto"""
        self.footer = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK, pady=5)
        self.footer.pack(fill=tk.X, padx=40, pady=5)
        
        # Crear una única fila con toda la información
        # Columna izquierda: Copyright
        self.footer_left = tk.Frame(self.footer, bg=SPOTIFY_BLACK)
        self.footer_left.pack(side=tk.LEFT, anchor='w')
        
        self.footer_text = tk.Label(
            self.footer_left,
            text="© 2025 Listify - V1.2.0",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9)
        )
        self.footer_text.pack(side=tk.LEFT)
        
        # Separador (texto de desarrollador)
        self.dev_text = tk.Label(
            self.footer,
            text="Desarrollado por Stef.dev",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9)
        )
        self.dev_text.pack(side=tk.LEFT, padx=20)
        
        # Columna derecha: Redes sociales en una sola línea
        self.footer_right = tk.Frame(self.footer, bg=SPOTIFY_BLACK)
        self.footer_right.pack(side=tk.RIGHT, anchor='e')
        
        self.social_label = tk.Label(
            self.footer_right,
            text="Síguenos en:",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9)
        )
        self.social_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Función para crear botones sociales
        def create_social_button(text, network):
            btn = tk.Button(
                self.footer_right,
                text=text,
                font=("Helvetica", 8),
                bg=SPOTIFY_BLACK,
                fg=SPOTIFY_LIGHT_GRAY,
                borderwidth=0,
                padx=3,
                pady=0,
                command=lambda: self.redes_callback(network)
            )
            btn.pack(side=tk.LEFT, padx=2)
            return btn
        
        # Crear botones para diferentes redes
        self.instagram_btn = create_social_button("Instagram", "instagram")
        self.github_btn = create_social_button("GitHub", "github")
        self.twitter_btn = create_social_button("Twitter", "twitter")
        self.linkedin_btn = create_social_button("LinkedIn", "linkedin")
    
    # Métodos funcionales
    def update_fullscreen_button(self, is_full):
        """Actualiza el texto del botón de pantalla completa"""
        if is_full:
            self.fullscreen_btn.config(text="Salir de Pantalla Completa")
        else:
            self.fullscreen_btn.config(text="Pantalla Completa")
    
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
        use_metadata = self.metadata_var.get()
        
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
            self.song_details_frame.pack_forget()
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
        """Actualiza la interfaz con los detalles de la canción (Mejorado)"""
        # Reiniciar estado
        self.shared_vars['status_text'].set("Listo")
        
        if not details:
            # Mostrar información básica si no hay detalles disponibles
            parts = track_name.split(" - ", 1)
            title = parts[0].strip()
            artist = parts[1].strip() if len(parts) > 1 else "Desconocido"
            
            self.song_title_label.config(text=title)
            self.artist_label.config(text=artist)
            self.album_label.config(text="N/A")
            self.release_label.config(text="N/A")
            self.duration_label.config(text="N/A")
            self.popularity_label.config(text="N/A")
        else:
            # Actualizar todos los campos
            self.song_title_label.config(text=details['name'])
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
        
        # Mostrar el frame de detalles
        self.song_details_frame.pack(fill=tk.X, pady=5, anchor='w')