#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Servicio de YouTube
"""
import os
import re
import time
from tkinter import messagebox
from youtubesearchpython import VideosSearch
import yt_dlp

def search_youtube(query, limit=1):
    """
    Busca un video en YouTube
    
    Args:
        query (str): Término de búsqueda
        limit (int, optional): Límite de resultados. Por defecto es 1.
    
    Returns:
        dict: Primer resultado de búsqueda
    """
    try:
        search = VideosSearch(query, limit=limit)
        results = search.result()
        return results['result'][0] if results['result'] else None
    except Exception as e:
        print(f"Error al buscar en YouTube: {e}")
        return None

def download_audio(video_url, output_path, filename):
    """
    Descarga el audio de un video de YouTube
    
    Args:
        video_url (str): URL del video
        output_path (str): Ruta de salida
        filename (str): Nombre del archivo
    
    Returns:
        bool: True si se descargó correctamente, False en caso contrario
    """
    try:
        # Sanitizar nombre de archivo
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", filename)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, f"{safe_name}.mp3"),
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
        
        return True
    except Exception as e:
        print(f"Error al descargar audio: {e}")
        return False

def download_tracks(tracks, destino, root, shared_vars):
    """
    Descarga una lista de pistas
    
    Args:
        tracks (list): Lista de nombres de pistas
        destino (str): Carpeta destino
        root (tk.Tk): Objeto raíz de tkinter
        shared_vars (dict): Variables compartidas
    """
    total = len(tracks)
    for index, track_name in enumerate(tracks):
        current = index + 1
        root.after(0, lambda: shared_vars['current_task'].set(f"Descargando ({current}/{total}): {track_name}"))
        root.after(0, lambda: shared_vars['progress_var'].set((current / total) * 100))
        root.after(0, lambda: shared_vars['status_text'].set(f"Buscando en YouTube..."))
        
        try:
            video = search_youtube(track_name)
            if video:
                video_url = video['link']
                
                root.after(0, lambda: shared_vars['status_text'].set(f"Descargando {current}/{total}..."))
                
                success = download_audio(video_url, destino, track_name)
                
                if success:
                    root.after(0, lambda msg=f"Descarga completada: {track_name}": shared_vars['status_text'].set(msg))
                else:
                    root.after(0, lambda msg=f"Error al descargar: {track_name}": shared_vars['status_text'].set(msg))
            else:
                root.after(0, lambda msg=f"No se encontró: {track_name}": shared_vars['status_text'].set(msg))
        except Exception as e:
            root.after(0, lambda msg=f"Error: {str(e)}": shared_vars['status_text'].set(msg))
            time.sleep(2)
    
    root.after(0, lambda: shared_vars['current_task'].set(f"Descarga finalizada"))
    root.after(0, lambda: shared_vars['status_text'].set(f"Se completaron {total} descargas"))
    
    # Mostrar mensaje final
    if total > 1:
        root.after(0, lambda: messagebox.showinfo("Descarga completada", f"Se han descargado {total} canciones correctamente."))
    else:
        root.after(0, lambda: messagebox.showinfo("Descarga completada", "Canción descargada correctamente."))