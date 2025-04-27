#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Pantalla de reproductor de música
"""
import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from io import BytesIO
import threading
import time

from config import SPOTIFY_BLACK, SPOTIFY_GREEN, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY

class PlayerScreen:
    """Clase para la pantalla del reproductor de música"""
    def __init__(self, parent, shared_vars, volver_callback, music_player):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=SPOTIFY_BLACK)
        self.shared_vars = shared_vars
        self.volver_callback = volver_callback
        
        # Usar el servicio de reproductor pasado como parámetro
        self.player = music_player
        
        # Variables de control
        self.music_folder = tk.StringVar(value="No seleccionado")
        self.current_song_title = tk.StringVar(value="Sin reproducción")
        self.current_song_artist = tk.StringVar(value="")
        self.current_song_album = tk.StringVar(value="")
        self.current_time_text = tk.StringVar(value="00:00")
        self.total_time_text = tk.StringVar(value="00:00")
        self.song_progress = tk.DoubleVar(value=0)
        self.updating_progress = False
        self.default_cover = None
        self.current_cover_image = None
        
        # Estado de reproducción
        self.is_playing = False
        self.update_ui_thread = None
        self.ui_thread_running = False
        
        # Crear la interfaz
        self._create_widgets()
        
        # Cargar un icono por defecto para la portada
        self._load_default_cover()
    
    def _create_widgets(self):
        """Crear los widgets de la pantalla del reproductor"""
        # Contenedor principal
        self.main_container = tk.Frame(self.frame, bg=SPOTIFY_BLACK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === HEADER ===
        self._create_header()
        
        # Contenedor para el contenido principal
        self.content_container = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.content_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Dividir en dos secciones
        self.left_panel = tk.Frame(self.content_container, bg=SPOTIFY_BLACK, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel.pack_propagate(False)  # Mantener el ancho fijo
        
        self.right_panel = tk.Frame(self.content_container, bg=SPOTIFY_BLACK)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # === PANEL IZQUIERDO (LISTA DE CANCIONES) ===
        self._create_playlist_panel()
        
        # === PANEL DERECHO (REPRODUCTOR) ===
        self._create_player_panel()
        
        # === CONTROLES DE REPRODUCCIÓN ===
        self._create_playback_controls()
    
    def _create_header(self):
        """Crear el encabezado con título y botón de volver"""
        self.header_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título
        self.title_label = tk.Label(
            self.header_frame, 
            text="Reproductor de Música", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Botón volver
        self.back_btn = tk.Button(
            self.header_frame, 
            text="Volver", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=15, 
            pady=5,
            borderwidth=0,
            command=self._on_close
        )
        self.back_btn.pack(side=tk.RIGHT)
        
        # Agregar efectos hover
        self.back_btn.bind("<Enter>", self._on_enter)
        self.back_btn.bind("<Leave>", self._on_leave)
    
    def _create_playlist_panel(self):
        """Crear el panel izquierdo con la lista de canciones"""
        # Sección para seleccionar carpeta
        self.folder_frame = tk.Frame(self.left_panel, bg=SPOTIFY_BLACK)
        self.folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_btn = tk.Button(
            self.folder_frame, 
            text="Seleccionar carpeta", 
            font=("Helvetica", 10),
            bg=SPOTIFY_DARK_GRAY, 
            fg="white", 
            padx=10, 
            pady=5,
            borderwidth=0,
            command=self._select_music_folder
        )
        self.folder_btn.pack(side=tk.LEFT)
        
        # Mostrar carpeta seleccionada
        self.folder_label = tk.Label(
            self.left_panel,
            textvariable=self.music_folder,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9),
            anchor="w",
            wraplength=280
        )
        self.folder_label.pack(fill=tk.X, pady=(0, 10))
        
        # Lista de canciones
        self.songs_label = tk.Label(
            self.left_panel, 
            text="Tu Música", 
            fg="white", 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 14, "bold"),
            anchor="w"
        )
        self.songs_label.pack(fill=tk.X, pady=(0, 5))
        
        # Frame para la lista con borde
        self.list_frame = tk.Frame(
            self.left_panel, 
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
        self.song_list = tk.Listbox(
            self.list_container, 
            font=("Helvetica", 10),
            bg=SPOTIFY_BLACK,
            fg="white",
            selectbackground=SPOTIFY_GREEN,
            activestyle='none',
            yscrollcommand=self.scrollbar.set,
            borderwidth=0,
            highlightthickness=0
        )
        self.song_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.song_list.yview)
        
        # Enlazar evento de selección
        self.song_list.bind('<<ListboxSelect>>', self._on_song_select)
        
        # Añadir efectos hover
        self.folder_btn.bind("<Enter>", self._on_enter)
        self.folder_btn.bind("<Leave>", self._on_leave)
    
    def _create_player_panel(self):
        """Crear el panel derecho con el reproductor"""
        # Contenedor para centrar la portada
        self.cover_container = tk.Frame(self.right_panel, bg=SPOTIFY_BLACK)
        self.cover_container.pack(fill=tk.BOTH, expand=True)
        
        # Crear un frame interno para centrar verticalmente
        self.centered_container = tk.Frame(self.cover_container, bg=SPOTIFY_BLACK)
        self.centered_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Portada grande
        self.cover_frame = tk.Frame(
            self.centered_container, 
            bg=SPOTIFY_BLACK, 
            width=300, 
            height=300,
            highlightbackground=SPOTIFY_DARK_GRAY,
            highlightthickness=1
        )
        self.cover_frame.pack(pady=(0, 20))
        self.cover_frame.pack_propagate(False)  # Mantener el tamaño fijo
        
        self.cover_label = tk.Label(self.cover_frame, bg=SPOTIFY_BLACK)
        self.cover_label.pack(fill=tk.BOTH, expand=True)
        
        # Información de la canción
        self.song_info_frame = tk.Frame(self.centered_container, bg=SPOTIFY_BLACK)
        self.song_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título de la canción
        self.song_title_label = tk.Label(
            self.song_info_frame,
            textvariable=self.current_song_title,
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 16, "bold"),
            anchor="center",
        )
        self.song_title_label.pack(fill=tk.X)
        
        # Artista
        self.song_artist_label = tk.Label(
            self.song_info_frame,
            textvariable=self.current_song_artist,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 12),
            anchor="center"
        )
        self.song_artist_label.pack(fill=tk.X)
        
        # Álbum
        self.song_album_label = tk.Label(
            self.song_info_frame,
            textvariable=self.current_song_album,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10, "italic"),
            anchor="center"
        )
        self.song_album_label.pack(fill=tk.X)
    
    def _create_playback_controls(self):
        """Crear los controles de reproducción en la parte inferior"""
        # Frame para la barra de progreso
        self.progress_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.progress_frame.pack(fill=tk.X, pady=(20, 5))
        
        # Etiqueta de tiempo actual
        self.current_time_label = tk.Label(
            self.progress_frame,
            textvariable=self.current_time_text,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9)
        )
        self.current_time_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Barra de progreso
        self.progress_bar = ttk.Scale(
            self.progress_frame,
            variable=self.song_progress,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_progress_change
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Etiqueta de tiempo total
        self.total_time_label = tk.Label(
            self.progress_frame,
            textvariable=self.total_time_text,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 9)
        )
        self.total_time_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones de control
        self.control_frame = tk.Frame(self.main_container, bg=SPOTIFY_BLACK)
        self.control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Frame para centrar los controles
        self.centered_controls = tk.Frame(self.control_frame, bg=SPOTIFY_BLACK)
        self.centered_controls.pack(pady=10)
        
        # Botón anterior
        self.prev_btn = tk.Button(
            self.centered_controls,
            text="⏮️",  # Icono Unicode para anterior
            font=("Helvetica", 14),
            bg=SPOTIFY_BLACK,
            fg="white",
            borderwidth=0,
            command=self._play_previous
        )
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón reproducir/pausar
        self.play_btn = tk.Button(
            self.centered_controls,
            text="▶️",  # Icono Unicode para reproducir
            font=("Helvetica", 18),
            bg=SPOTIFY_BLACK,
            fg="white",
            borderwidth=0,
            command=self._toggle_play
        )
        self.play_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón detener
        self.stop_btn = tk.Button(
            self.centered_controls,
            text="⏹️",  # Icono Unicode para detener
            font=("Helvetica", 14),
            bg=SPOTIFY_BLACK,
            fg="white",
            borderwidth=0,
            command=self._stop_playback
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón siguiente
        self.next_btn = tk.Button(
            self.centered_controls,
            text="⏭️",  # Icono Unicode para siguiente
            font=("Helvetica", 14),
            bg=SPOTIFY_BLACK,
            fg="white",
            borderwidth=0,
            command=self._play_next
        )
        self.next_btn.pack(side=tk.LEFT, padx=10)
        
        # Añadir efectos hover
        for btn in [self.prev_btn, self.play_btn, self.stop_btn, self.next_btn]:
            btn.bind("<Enter>", self._on_enter_control)
            btn.bind("<Leave>", self._on_leave_control)
    
    def _select_music_folder(self):
        """Permite al usuario seleccionar una carpeta de música"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.music_folder.set(folder_selected)
            self._load_songs_from_folder(folder_selected)
    
    def _load_songs_from_folder(self, folder):
        """Carga las canciones de la carpeta seleccionada"""
        self.song_list.delete(0, tk.END)
        
        # Buscar archivos MP3 en la carpeta
        mp3_files = self.player.scan_directory(folder)
        
        if not mp3_files:
            self.song_list.insert(tk.END, "No se encontraron archivos MP3")
            return
        
        # Cargar la playlist en el reproductor
        self.player.load_playlist(mp3_files)
        
        # Mostrar los nombres de archivo sin la ruta completa
        for file_path in mp3_files:
            filename = os.path.basename(file_path)
            name_only = os.path.splitext(filename)[0]
            self.song_list.insert(tk.END, name_only)
    
    def _on_song_select(self, event):
        """Maneja la selección de una canción en la lista"""
        if not self.song_list.curselection():
            return
        
        selected_index = self.song_list.curselection()[0]
        self._play_song(index=selected_index)
    
    def _play_song(self, index=None):
        """Reproduce la canción seleccionada"""
        if not hasattr(self.player, 'playlist') or not self.player.playlist:
            return
        
        # Reproducir la canción
        metadata = self.player.play(index=index)
        
        if metadata:
            # Actualizar UI con metadatos
            self.current_song_title.set(metadata['title'])
            self.current_song_artist.set(metadata['artist'])
            self.current_song_album.set(metadata['album'])
            
            # Actualizar portada
            self._update_cover(metadata['cover'])
            
            # Actualizar tiempo total
            total_length = self.player.get_length()
            mins, secs = divmod(int(total_length), 60)
            self.total_time_text.set(f"{mins:02d}:{secs:02d}")
            
            # Cambiar icono de reproducción a pausa
            self.play_btn.config(text="⏸️")
            
            # Iniciar actualización de UI
            self._start_ui_update()
    
    def _toggle_play(self):
        """Alterna entre reproducir y pausar"""
        if not hasattr(self.player, 'playlist') or not self.player.playlist:
            return
        
        if self.player.is_paused():
            # Reanudar reproducción
            self.player.resume()
            self.play_btn.config(text="⏸️")
            # Asegurarse de que la UI se esté actualizando
            self._start_ui_update()
        elif self.player.is_playing():
            # Pausar reproducción
            self.player.pause()
            self.play_btn.config(text="▶️")
        else:
            # No hay reproducción activa, intentar reproducir la primera canción
            if self.song_list.size() > 0:
                self.song_list.selection_clear(0, tk.END)
                self.song_list.selection_set(0)
                self._play_song(index=0)
    
    def _stop_playback(self):
        """Detiene la reproducción actual"""
        self.player.stop()
        self.play_btn.config(text="▶️")
        self.current_time_text.set("00:00")
        self.song_progress.set(0)
        self._stop_ui_update()
    
    def _play_next(self):
        """Reproduce la siguiente canción en la lista"""
        metadata = self.player.play_next()
        if metadata:
            # Actualizar selección en la lista
            current_index = self.player.current_index
            if current_index >= 0:
                self.song_list.selection_clear(0, tk.END)
                self.song_list.selection_set(current_index)
                self.song_list.see(current_index)  # Asegurar que sea visible
            
            # Actualizar UI
            self.current_song_title.set(metadata['title'])
            self.current_song_artist.set(metadata['artist'])
            self.current_song_album.set(metadata['album'])
            
            # Actualizar portada
            self._update_cover(metadata['cover'])
            
            # Actualizar tiempo total
            total_length = self.player.get_length()
            mins, secs = divmod(int(total_length), 60)
            self.total_time_text.set(f"{mins:02d}:{secs:02d}")
            
            # Cambiar icono de reproducción a pausa
            self.play_btn.config(text="⏸️")
            
            # Reiniciar la actualización de UI
            self._start_ui_update()
    
    def _play_previous(self):
        """Reproduce la canción anterior en la lista"""
        metadata = self.player.play_previous()
        if metadata:
            # Actualizar selección en la lista
            current_index = self.player.current_index
            if current_index >= 0:
                self.song_list.selection_clear(0, tk.END)
                self.song_list.selection_set(current_index)
                self.song_list.see(current_index)  # Asegurar que sea visible
            
            # Actualizar UI
            self.current_song_title.set(metadata['title'])
            self.current_song_artist.set(metadata['artist'])
            self.current_song_album.set(metadata['album'])
            
            # Actualizar portada
            self._update_cover(metadata['cover'])
            
            # Actualizar tiempo total
            total_length = self.player.get_length()
            mins, secs = divmod(int(total_length), 60)
            self.total_time_text.set(f"{mins:02d}:{secs:02d}")
            
            # Cambiar icono de reproducción a pausa
            self.play_btn.config(text="⏸️")
            
            # Reiniciar la actualización de UI
            self._start_ui_update()

    def _on_progress_change(self, value):
        """Maneja cambios en la barra de progreso por interacción del usuario"""
        if self.updating_progress or not hasattr(self.player, 'playlist') or not self.player.playlist:
            return
        
        # Convertir de porcentaje (0-100) a decimal (0.0-1.0)
        percentage = float(value) / 100.0
        
        # Buscar la posición en la canción
        self.player.seek_percentage(percentage)
        
        # Actualizar el tiempo mostrado
        current_time = self.player.get_position()
        mins, secs = divmod(int(current_time), 60)
        self.current_time_text.set(f"{mins:02d}:{secs:02d}")
    
    def _update_cover(self, cover_data):
        """Actualiza la imagen de portada"""
        try:
            if cover_data:
                # Crear imagen desde los datos binarios
                img = Image.open(BytesIO(cover_data))
                img = img.resize((298, 298), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cover_label.config(image=photo)
                self.current_cover_image = photo  # Mantener referencia para evitar recolección de basura
            else:
                # Mostrar imagen por defecto
                self.cover_label.config(image=self.default_cover)
                self.current_cover_image = self.default_cover
        except Exception as e:
            print(f"Error al actualizar portada: {e}")
            # Mostrar imagen por defecto en caso de error
            self.cover_label.config(image=self.default_cover)
            self.current_cover_image = self.default_cover
    
    def _load_default_cover(self):
        """Carga una imagen por defecto para la portada"""
        try:
            # Crear una imagen de color sólido con el logotipo de Listify
            img = Image.new('RGB', (298, 298), color=SPOTIFY_DARK_GRAY)
            
            # Guardar referencia a la imagen
            self.default_cover = ImageTk.PhotoImage(img)
            self.cover_label.config(image=self.default_cover)
        except Exception as e:
            print(f"Error al cargar portada por defecto: {e}")
    
    def _start_ui_update(self):
        """Inicia el hilo de actualización de la UI"""
        self.ui_thread_running = True
        if self.update_ui_thread and self.update_ui_thread.is_alive():
            return
            
        self.update_ui_thread = threading.Thread(target=self._update_ui_thread, daemon=True)
        self.update_ui_thread.start()
    
    def _stop_ui_update(self):
        """Detiene el hilo de actualización de la UI"""
        self.ui_thread_running = False
    
    def _update_ui_thread(self):
        """Hilo para actualizar la UI durante la reproducción"""
        while self.ui_thread_running:
            if not self.player.is_playing() and not self.player.is_paused():
                # La reproducción se ha detenido
                self.ui_thread_running = False
                break
            
            # Obtener posición actual y actualizar la UI
            current_position = self.player.get_position()
            song_length = max(0.1, self.player.get_length())  # Evitar división por cero
            
            # Calcular porcentaje y tiempo formateado
            percentage = (current_position / song_length) * 100
            mins, secs = divmod(int(current_position), 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            # Actualizar elementos de la UI en el hilo principal
            self.parent.after(10, lambda p=percentage, t=time_str: self._update_progress_ui(p, t))
            
            # Pequeña pausa para no sobrecargar
            time.sleep(0.1)
    
    def _update_progress_ui(self, percentage, time_str):
        """Actualiza los elementos de progreso en la UI (llamado desde el hilo principal)"""
        self.updating_progress = True
        self.song_progress.set(percentage)
        self.current_time_text.set(time_str)
        self.updating_progress = False
    
    def _on_enter(self, e):
        """Efecto al pasar el mouse sobre un botón normal"""
        e.widget.config(bg="#444444", cursor="hand2")
    
    def _on_leave(self, e):
        """Efecto al quitar el mouse de un botón normal"""
        e.widget.config(bg=SPOTIFY_DARK_GRAY)
    
    def _on_enter_control(self, e):
        """Efecto al pasar el mouse sobre un botón de control"""
        e.widget.config(fg=SPOTIFY_GREEN, cursor="hand2")
    
    def _on_leave_control(self, e):
        """Efecto al quitar el mouse de un botón de control"""
        e.widget.config(fg="white")
    
    def _on_close(self):
        """Acciones a realizar al cerrar la pantalla"""
        # Ya no detenemos la reproducción, sólo paramos la actualización de UI
        self._stop_ui_update()
        
        # Volver a la pantalla anterior
        self.volver_callback()
    
    def refresh_player_view(self):
        """Actualiza la interfaz del reproductor cuando se regresa a esta pantalla"""
        # Actualizar lista de canciones si es necesario
        if self.music_folder.get() != "No seleccionado":
            self._load_songs_from_folder(self.music_folder.get())
        
        # Si hay reproducción activa, actualizar UI
        if not self.player.stopped:
            # Obtener metadatos de la canción actual
            if self.player.current_song:
                metadata = self.player.get_song_metadata(self.player.current_song)
                
                # Actualizar información mostrada
                self.current_song_title.set(metadata['title'])
                self.current_song_artist.set(metadata['artist'])
                self.current_song_album.set(metadata['album'])
                
                # Actualizar portada
                self._update_cover(metadata['cover'])
                
                # Actualizar tiempo total
                total_length = self.player.get_length()
                mins, secs = divmod(int(total_length), 60)
                self.total_time_text.set(f"{mins:02d}:{secs:02d}")
                
                # Actualizar icono del botón según estado
                if self.player.is_paused():
                    self.play_btn.config(text="▶️")
                else:
                    self.play_btn.config(text="⏸️")
                    # Reiniciar la actualización de UI si está reproduciendo
                    self._start_ui_update()
            
            # Actualizar selección en la lista
            if hasattr(self.player, 'current_index') and self.player.current_index >= 0:
                try:
                    self.song_list.selection_clear(0, tk.END)
                    self.song_list.selection_set(self.player.current_index)
                    self.song_list.see(self.player.current_index)
                except:
                    pass  # Por si el índice está fuera de rango