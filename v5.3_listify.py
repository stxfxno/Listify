import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from youtubesearchpython import VideosSearch
import yt_dlp
import os
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de Spotify
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Colores y estilos
SPOTIFY_GREEN = "#1DB954"
SPOTIFY_BLACK = "#191414"
SPOTIFY_DARK_GRAY = "#333333"
SPOTIFY_LIGHT_GRAY = "#B3B3B3"

class ListifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Listify")
        self.root.geometry("850x850")
        self.root.configure(bg=SPOTIFY_BLACK)
        self.root.minsize(850, 850)
        
        # Icono de la aplicación (placeholder si no tienes uno)
        try:
            icon = Image.open(BytesIO(requests.get("https://www.freepnglogos.com/uploads/spotify-logo-png/file-spotify-logo-png-4.png").content))
            photo = ImageTk.PhotoImage(icon)
            self.root.iconphoto(False, photo)
        except:
            pass
        
        # Variables
        self.destino_var = tk.StringVar(value="No seleccionado")
        self.current_task = tk.StringVar(value="")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.playlist_title = tk.StringVar(value="")
        self.status_text = tk.StringVar(value="Listo para descargar")
        
        # Crear frames
        self.create_splash_screen()
        self.create_frames()
        self.setup_styles()
        
        # Iniciar con la pantalla de inicio
        self.mostrar_splash()

    #####

    def search_spotify(self):
        search_query = self.search_entry.get().strip()
        search_type = self.search_type.get().lower()
        
        if not search_query:
            messagebox.showwarning("Advertencia", "Por favor ingresa un término de búsqueda.")
            return
        
        # Mostrar indicador de carga
        self.status_text.set(f"Buscando {search_type} en Spotify...")
        self.track_list.delete(0, tk.END)
        self.playlist_title.set("")
        self.cover_label.config(image="")
        self.progress_var.set(20)
        self.root.update()
        
        # Ejecutar en un hilo separado para no congelar la UI
        threading.Thread(target=self._search_spotify_thread, 
                    args=(search_query, search_type), 
                    daemon=True).start()

    def _search_spotify_thread(self, query, search_type):
        results, cover_url, title = self.perform_spotify_search(query, search_type)
        
        # Actualizar la UI en el hilo principal
        self.root.after(0, lambda: self._update_search_ui(results, cover_url, title))

    def _update_search_ui(self, results, cover_url, title):
        if results:
            for item in results:
                self.track_list.insert(tk.END, item)
            
            self.playlist_title.set(title)
            
            if cover_url:
                try:
                    response = requests.get(cover_url)
                    img_data = BytesIO(response.content)
                    cover_img = Image.open(img_data).resize((150, 150), Image.LANCZOS)
                    cover_photo = ImageTk.PhotoImage(cover_img)
                    self.cover_label.config(image=cover_photo)
                    self.cover_label.image = cover_photo
                except Exception as e:
                    print(f"Error al cargar la portada: {e}")
        
        self.progress_var.set(100)
        self.status_text.set(f"Listo - {len(results)} resultados encontrados")
        
        # Reiniciar la barra de progreso después de un tiempo
        self.root.after(3000, lambda: self.progress_var.set(0))

    def perform_spotify_search(self, query, search_type):
        client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        results = []
        cover_url = None
        title = f"Resultados para: {query}"
        
        try:
            if search_type == "canciones":
                spotify_type = "track"
                response = sp.search(q=query, type=spotify_type, limit=50)
                items = response['tracks']['items']
                for item in items:
                    results.append(f"{item['name']} - {', '.join(artist['name'] for artist in item['artists'])}")
                if items and items[0]['album']['images']:
                    cover_url = items[0]['album']['images'][0]['url']
            
            elif search_type == "artistas":
                spotify_type = "artist"
                response = sp.search(q=query, type=spotify_type, limit=20)
                items = response['artists']['items']
                for item in items:
                    results.append(f"{item['name']} - Artista")
                    # Obtener los top tracks del primer artista
                    if items and items[0]['id'] and not results:
                        top_tracks = sp.artist_top_tracks(items[0]['id'])
                        for track in top_tracks['tracks']:
                            results.append(f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
                if items and items[0]['images']:
                    cover_url = items[0]['images'][0]['url']
            
            elif search_type == "álbumes":
                spotify_type = "album"
                response = sp.search(q=query, type=spotify_type, limit=20)
                items = response['albums']['items']
                
                for album in items:
                    results.append(f"ÁLBUM: {album['name']} - {', '.join(artist['name'] for artist in album['artists'])}")
                    
                    # Obtener las canciones del álbum
                    album_tracks = sp.album_tracks(album['id'])
                    for track in album_tracks['items']:
                        results.append(f"  • {track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
                
                if items and items[0]['images']:
                    cover_url = items[0]['images'][0]['url']
            
            return results, cover_url, title
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error al buscar en Spotify: {e}"))
            return [], None, f"Error en la búsqueda: {query}"
    
    #####
        
    def create_splash_screen(self):
        self.splash_frame = tk.Frame(self.root, bg=SPOTIFY_BLACK)
        
        # Logo grande
        self.logo_label = tk.Label(
            self.splash_frame, 
            text="🎵 Listify", 
            fg=SPOTIFY_GREEN, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 48, "bold")
        )
        self.logo_label.pack(pady=100)
        
        # Eslogan
        self.slogan_label = tk.Label(
            self.splash_frame, 
            text="Tu música favorita, donde quieras", 
            fg=SPOTIFY_LIGHT_GRAY, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 16)
        )
        self.slogan_label.pack(pady=20)
        
        # Botones estilizados
        self.buttons_frame = tk.Frame(self.splash_frame, bg=SPOTIFY_BLACK)
        self.buttons_frame.pack(pady=50)
        
        self.inicio_btn = tk.Button(
            self.buttons_frame, 
            text="COMENZAR", 
            font=("Helvetica", 12, "bold"),
            bg=SPOTIFY_GREEN, 
            fg="white", 
            padx=20, 
            pady=10,
            borderwidth=0,
            command=self.abrir_inicio
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
            command=self.abrir_redes
        )
        self.redes_btn.pack(side=tk.LEFT, padx=10)
        
        # Footer
        self.footer_label = tk.Label(
            self.splash_frame, 
            text="Desarrollado por stef.dev_", 
            fg=SPOTIFY_LIGHT_GRAY, 
            bg=SPOTIFY_BLACK, 
            font=("Helvetica", 10)
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=20)
    
    def create_frames(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=SPOTIFY_BLACK)
        
        # Header con logo y navegación
        self.header_frame = tk.Frame(self.main_frame, bg=SPOTIFY_BLACK)
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
            command=self.volver_inicio
        )
        self.nav_btn.pack(side=tk.RIGHT, padx=10)
        
        # Contenedor central
        self.content_frame = tk.Frame(self.main_frame, bg=SPOTIFY_BLACK)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # Sección de URL
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

        #
        # Sección de búsqueda
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
        
        # Sección de info y portada
        self.info_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.cover_label = tk.Label(self.info_frame, bg=SPOTIFY_BLACK)
        self.cover_label.pack(side=tk.LEFT, padx=10)
        
        self.title_label = tk.Label(
            self.info_frame,
            textvariable=self.playlist_title,
            fg="white",
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 16, "bold"),
            wraplength=400
        )
        self.title_label.pack(side=tk.LEFT, padx=20, anchor='nw')
        
        # Lista de canciones con scrollbar
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
        
        # Sección de descarga
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
            command=self.seleccionar_destino
        )
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_label = tk.Label(
            self.folder_frame,
            textvariable=self.destino_var,
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
        
        # Barra de progreso
        self.progress_frame = tk.Frame(self.content_frame, bg=SPOTIFY_BLACK)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        self.current_task_label = tk.Label(
            self.progress_frame,
            textvariable=self.current_task,
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
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = tk.Label(
            self.progress_frame,
            textvariable=self.status_text,
            fg=SPOTIFY_LIGHT_GRAY,
            bg=SPOTIFY_BLACK,
            font=("Helvetica", 10),
            anchor='w'
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Footer
        self.footer = tk.Frame(self.main_frame, bg=SPOTIFY_BLACK)
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
            command=self.abrir_redes
        )
        self.social_btn.pack(side=tk.RIGHT)
    
    def setup_styles(self):
        # Configurar estilos para ttk widgets
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", 
                    thickness=10, 
                    troughcolor=SPOTIFY_DARK_GRAY,
                    background=SPOTIFY_GREEN)
        
        # Configurar estilo para el combobox
        style.configure("TCombobox", 
                    fieldbackground=SPOTIFY_DARK_GRAY,
                    background=SPOTIFY_DARK_GRAY,
                    foreground="white",
                    selectbackground=SPOTIFY_GREEN)
        
        # Configurar hover para botones
        for btn in [self.inicio_btn, self.redes_btn, self.nav_btn, 
                self.fetch_btn, self.folder_btn, 
                self.download_song_btn, self.download_playlist_btn,
                self.search_btn]:  # Añadir search_btn aquí
            btn.bind("<Enter>", self.on_enter)
            btn.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        if e.widget['bg'] == SPOTIFY_GREEN:
            e.widget['bg'] = "#1ED760"  # Verde más claro
        else:
            e.widget['bg'] = "#444444"  # Gris más claro
    
    def on_leave(self, e):
        if "#1ED760" in e.widget['bg']:
            e.widget['bg'] = SPOTIFY_GREEN
        else:
            e.widget['bg'] = SPOTIFY_DARK_GRAY
            
    def mostrar_splash(self):
        self.splash_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_forget()
        
    def abrir_inicio(self):
        self.splash_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def volver_inicio(self):
        self.main_frame.pack_forget()
        self.splash_frame.pack(fill=tk.BOTH, expand=True)
        
    def abrir_redes(self):
        webbrowser.open("https://www.instagram.com/stef.dev_/")
    
    def seleccionar_destino(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.destino_var.set(folder_selected)
    
    def fetch_tracks(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Advertencia", "Por favor ingresa una URL de Spotify.")
            return
        
        # Mostrar indicador de carga
        self.status_text.set("Obteniendo datos de Spotify...")
        self.track_list.delete(0, tk.END)
        self.playlist_title.set("")
        self.cover_label.config(image="")
        self.progress_var.set(20)
        self.root.update()
        
        # Ejecutar en un hilo separado para no congelar la UI
        threading.Thread(target=self._fetch_tracks_thread, args=(url,), daemon=True).start()
    
    def _fetch_tracks_thread(self, url):
        tracks, cover_url, title = self.get_tracks(url)
        
        # Actualizar la UI en el hilo principal
        self.root.after(0, lambda: self._update_tracks_ui(tracks, cover_url, title))
    
    def _update_tracks_ui(self, tracks, cover_url, title):
        if tracks:
            for track in tracks:
                self.track_list.insert(tk.END, track)
            
            self.playlist_title.set(title)
            
            if cover_url:
                try:
                    response = requests.get(cover_url)
                    img_data = BytesIO(response.content)
                    cover_img = Image.open(img_data).resize((150, 150), Image.LANCZOS)
                    cover_photo = ImageTk.PhotoImage(cover_img)
                    self.cover_label.config(image=cover_photo)
                    self.cover_label.image = cover_photo
                except Exception as e:
                    print(f"Error al cargar la portada: {e}")
        
        self.progress_var.set(100)
        self.status_text.set(f"Listo - {len(tracks)} canciones encontradas")
        
        # Reiniciar la barra de progreso después de un tiempo
        self.root.after(3000, lambda: self.progress_var.set(0))
        
    def get_tracks(self, url):
        client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        tracks = []
        cover_url = None
        title = ""
        
        try:
            if 'album' in url:
                album_id = re.search(r'album/([a-zA-Z0-9]+)', url).group(1)
                results = sp.album_tracks(album_id)
                album_info = sp.album(album_id)
                cover_url = album_info['images'][0]['url'] if album_info['images'] else None
                title = f"{album_info['name']} - {album_info['artists'][0]['name']}"
                for item in results['items']:
                    tracks.append(f"{item['name']} - {', '.join(artist['name'] for artist in item['artists'])}")
            elif 'playlist' in url:
                playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url).group(1)
                results = sp.playlist_tracks(playlist_id)
                playlist_info = sp.playlist(playlist_id)
                cover_url = playlist_info['images'][0]['url'] if playlist_info['images'] else None
                title = playlist_info['name']
                while results:
                    for item in results['items']:
                        track = item.get('track')
                        if track and track['type'] == 'track':
                            tracks.append(f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
                    results = sp.next(results) if results['next'] else None
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "URL inválida. Debe ser un álbum o playlist de Spotify."))
                return [], None, None
            return tracks, cover_url, title
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error al obtener datos de Spotify: {e}"))
            return [], None, None
        
    def descargar_cancion(self):
        selected_song = self.track_list.get(tk.ACTIVE)
        if not selected_song:
            messagebox.showwarning("Advertencia", "Selecciona una canción para descargar.")
            return
        
        threading.Thread(target=self._descargar_audio, args=([selected_song],), daemon=True).start()
    
    def descargar_playlist(self):
        if self.track_list.size() == 0:
            messagebox.showwarning("Advertencia", "No hay canciones en la lista.")
            return
        
        tracks = [self.track_list.get(i) for i in range(self.track_list.size())]
        threading.Thread(target=self._descargar_audio, args=(tracks,), daemon=True).start()
    
    def _descargar_audio(self, tracks):
        if not self.destino_var.get() or self.destino_var.get() == "No seleccionado":
            self.root.after(0, lambda: messagebox.showerror("Error", "Selecciona un destino primero."))
            return
        
        total = len(tracks)
        for index, track_name in enumerate(tracks):
            current = index + 1
            self.root.after(0, lambda: self.current_task.set(f"Descargando ({current}/{total}): {track_name}"))
            self.root.after(0, lambda: self.progress_var.set((current / total) * 100))
            self.root.after(0, lambda: self.status_text.set(f"Buscando en YouTube..."))
            
            try:
                search = VideosSearch(track_name, limit=1)
                result = search.result()
                if result['result']:
                    video_url = result['result'][0]['link']
                    download_folder = self.destino_var.get()
                    
                    # Sanitizar nombre de archivo
                    safe_name = re.sub(r'[\\/*?:"<>|]', "_", track_name)
                    
                    self.root.after(0, lambda: self.status_text.set(f"Descargando {current}/{total}..."))
                    
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(download_folder, f"{safe_name}.mp3"),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '320',
                        }],
                        'quiet': True,
                        'no_warnings': True
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    
                    self.root.after(0, lambda msg=f"Descarga completada: {track_name}": self.status_text.set(msg))
                else:
                    self.root.after(0, lambda msg=f"No se encontró: {track_name}": self.status_text.set(msg))
            except Exception as e:
                self.root.after(0, lambda msg=f"Error: {str(e)}": self.status_text.set(msg))
                time.sleep(2)
        
        self.root.after(0, lambda: self.current_task.set(f"Descarga finalizada"))
        self.root.after(0, lambda: self.status_text.set(f"Se completaron {total} descargas"))
        
        # Mostrar mensaje final
        if total > 1:
            self.root.after(0, lambda: messagebox.showinfo("Descarga completada", f"Se han descargado {total} canciones correctamente."))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Descarga completada", "Canción descargada correctamente."))

if __name__ == "__main__":
    root = tk.Tk()
    app = ListifyApp(root)
    root.mainloop()