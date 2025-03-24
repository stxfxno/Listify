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
from services.metadata_service import get_basic_metadata, add_metadata_to_file, fix_mp3_file

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

def download_audio(video_url, output_path, filename, cover_url=None, album_name=None):
    """
    Descarga el audio de un video de YouTube
    
    Args:
        video_url (str): URL del video
        output_path (str): Ruta de salida
        filename (str): Nombre del archivo
        cover_url (str, optional): URL de la imagen de portada
        album_name (str, optional): Nombre del álbum
    
    Returns:
        bool: True si se descargó correctamente, False en caso contrario
    """
    try:
        # Sanitizar nombre de archivo y eliminar .mp3 si ya está en el nombre
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", filename)
        if safe_name.lower().endswith('.mp3'):
            safe_name = safe_name[:-4]
        
        # Normalizar la ruta
        output_path = os.path.normpath(output_path)
        output_file = os.path.normpath(os.path.join(output_path, f"{safe_name}.mp3"))
        
        # Verificar que el directorio de salida existe
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
        
        # Eliminar el archivo si ya existe
        if os.path.exists(output_file):
            os.remove(output_file)
            
        # También verificar y eliminar si existe con doble extensión
        double_ext_file = f"{output_file}.mp3"
        if os.path.exists(double_ext_file):
            os.remove(double_ext_file)
        
        # Opciones para yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
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
        
        # Esperar un momento para que el sistema de archivos se actualice
        time.sleep(1)
        
        # Verificar archivos y corregir extensiones
        if os.path.exists(output_file):
            pass
        elif os.path.exists(double_ext_file):
            os.rename(double_ext_file, output_file)
        else:
            # Buscar cualquier archivo que comience con el nombre base
            base_dir = os.path.dirname(output_file)
            base_name = os.path.splitext(os.path.basename(output_file))[0]
            
            potential_files = [f for f in os.listdir(base_dir) if f.startswith(base_name)]
            
            if potential_files:
                found_file = os.path.join(base_dir, potential_files[0])
                
                if found_file != output_file:
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    os.rename(found_file, output_file)
            else:
                return False
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(output_file) / (1024*1024)
        if file_size < 0.1:
            return False
        
        # Intentar reparar el archivo MP3 si es necesario
        fix_mp3_file(output_file)
        
        # Añadir metadatos al archivo MP3
        metadata = get_basic_metadata(filename, cover_url, album_name)
        
        # Esperar un momento para asegurarse de que el archivo está disponible
        time.sleep(1)
        
        add_metadata_to_file(output_file, metadata)
        
        return True
    except Exception as e:
        print(f"Error al descargar audio: {e}")
        return False

def download_tracks(tracks, destino, root, shared_vars, cover_url=None, album_name=None):
    """
    Descarga una lista de pistas
    
    Args:
        tracks (list): Lista de nombres de pistas
        destino (str): Carpeta destino
        root (tk.Tk): Objeto raíz de tkinter
        shared_vars (dict): Variables compartidas
        cover_url (str, optional): URL de la imagen de portada
        album_name (str, optional): Nombre del álbum
    """
    # Normalizar la ruta de destino
    destino = os.path.normpath(destino)
    
    total = len(tracks)
    for index, track_name in enumerate(tracks):
        current = index + 1
        # Usar variables locales en las lambdas para capturar correctamente los valores
        current_num = current 
        total_num = total
        track_display = track_name
        
        root.after(0, lambda c=current_num, t=total_num, n=track_display: 
                    shared_vars['current_task'].set(f"Descargando ({c}/{t}): {n}"))
        root.after(0, lambda c=current_num, t=total_num: 
                    shared_vars['progress_var'].set((c / t) * 100))
        root.after(0, lambda: 
                    shared_vars['status_text'].set(f"Buscando en YouTube..."))
        
        try:
            video = search_youtube(track_name)
            if video:
                video_url = video['link']
                
                root.after(0, lambda c=current_num, t=total_num: 
                           shared_vars['status_text'].set(f"Descargando {c}/{t}..."))
                
                success = download_audio(video_url, destino, track_name, cover_url, album_name)
                
                if success:
                    root.after(0, lambda n=track_display: 
                               shared_vars['status_text'].set(f"Descarga completada: {n}"))
                else:
                    root.after(0, lambda n=track_display: 
                               shared_vars['status_text'].set(f"Error al descargar: {n}"))
            else:
                root.after(0, lambda n=track_display: 
                           shared_vars['status_text'].set(f"No se encontró: {n}"))
        except Exception as e:
            error_msg = str(e)
            root.after(0, lambda err=error_msg: 
                       shared_vars['status_text'].set(f"Error: {err}"))
            time.sleep(2)
    
    root.after(0, lambda: shared_vars['current_task'].set(f"Descarga finalizada"))
    root.after(0, lambda: shared_vars['status_text'].set(f"Se completaron {total} descargas"))
    
    # Mostrar mensaje final
    if total > 1:
        root.after(0, lambda: messagebox.showinfo("Descarga completada", 
                                                f"Se han descargado {total} canciones correctamente."))
    else:
        root.after(0, lambda: messagebox.showinfo("Descarga completada", 
                                                "Canción descargada correctamente."))