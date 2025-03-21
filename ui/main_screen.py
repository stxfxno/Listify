#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Pantalla principal
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from ..config import SPOTIFY_BLACK, SPOTIFY_GREEN, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY
from services.spotify_service import search_spotify, get_tracks_from_url
from services.youtube_service import download_tracks

class MainScreen:
    """Clase para la pantalla principal de la aplicación"""
    def __init__(self, parent, shared_vars, volver_callback, redes_callback, destino_callback):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=SPOTIFY_BLACK)
        
        # Variables compartidas
        self.shared_vars = shared_vars
        
        # Callbacks
        self.volver_callback = volver_callback
        self.redes_callback = redes_callback
        self.destino_callback = destino_callback
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear los widgets de la pantalla principal"""
        # Header con logo y navegación
        self._create_header()
        
        # Contenedor central
        self.content_frame = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
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
    
    def _create_header(self):
        """Crear el encabezado con logo y navegación"""
        self.header_frame = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.small_logo = tk.Label(
            self.header_frame, 
            text="🎵 Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 18, "bold")
        )
        self.small_logo.pack(side=tk.LEFT, padx=10)
        
        self.nav_btn = tk.Button(
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
        self.nav_btn.pack(side=tk.RIGHT, padx=10)
    
    def _create_url_section(self):
        """Crear la sección de entrada de URL"""
        self.url_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.url_frame.pack(fill=tk.X, pady=10)
        
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
        self.search_frame.pack(fill=tk.X, pady=10)

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
        """Crear la sección de información y portada"""
        self.info_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.cover_label = tk.Label(self.info_frame, bg=SPOTIFY_BLACK)
        self.cover_label.pack(side=tk.LEFT, padx=10)
        
        self.title_label = tk.Label(
            self.info_frame,
            textvariable=self.shared_vars['playlist_title'],
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 16, "bold"),
            wraplength=400
        )
        self.title_label.pack(side=tk.LEFT, padx=20, anchor='nw')
    
    def _create_tracklist_section(self):
        """Crear la sección de lista de canciones"""
        self.list_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
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
        
        self.track_list = tk.Listbox(
            self.list_container, 
            width=60, 
            height=12,
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY,
            fg="white",
            selectbackground=SPOTIFY_GREEN,
            activestyle='none',
            yscrollcommand=self.scrollbar.set
        )
        self.track_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.track_list.yview)
    
    def _create_download_section(self):
        """Crear la sección de descarga"""
        self.download_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.download_frame.pack(fill=tk.X, pady=10)
        
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
        self.progress_frame.pack(fill=tk.X, pady=5)
        
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
        """Crear el pie de página"""
        self.footer = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.footer.pack(fill=tk.X, padx=20, pady=10)
        
        self.footer_text = tk.Label(
            self.footer,
            text="© 2025 Listify - Desarrollado por stef.dev_",
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 8)
        )
        self.footer_text.pack(side=tk.LEFT)
        
        self.social_btn = tk.Button(
            self.footer,
            text="Instagram",
            font=("Helvetica", 8),
            bg=SPOTIFY_BLACK,
            fg=SPOTIFY_LIGHT_GRAY,
            borderwidth=0,
            padx=5,
            pady=0,
            command=self.redes_callback
        )
        self.social_btn.pack(side=tk.RIGHT)
    
    # Métodos funcionales
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
        
        # Ejecutar en un hilo separado para no congelar la UI
        threading.Thread(target=self._fetch_tracks_thread, args=(url,), daemon=True).start()
    
    def _fetch_tracks_thread(self, url):
        """Hilo para obtener pistas de Spotify"""
        tracks, cover_url, title = get_tracks_from_url(url)
        
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
        
        # Ejecutar en un hilo separado para no congelar la UI
        threading.Thread(target=self._search_spotify_thread, 
                     args=(search_query, search_type), 
                     daemon=True).start()

    def _search_spotify_thread(self, query, search_type):
        """Hilo para buscar en Spotify"""
        results, cover_url, title = search_spotify(query, search_type)
        
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
        
        download_tracks(tracks, destino, self.parent, self.shared_vars)