#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Servicio de YouTube
"""
import os
import re
import time
import logging
from tkinter import messagebox
from youtubesearchpython import VideosSearch
import yt_dlp
from services.metadata_service import get_basic_metadata, add_metadata_to_file, fix_mp3_file

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube_service')

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
        logger.info(f"Buscando en YouTube: '{query}'")
        search = VideosSearch(query, limit=limit)
        results = search.result()
        if results['result']:
            logger.info(f"Resultado encontrado: {results['result'][0]['title']}")
            return results['result'][0]
        else:
            logger.warning(f"No se encontraron resultados para: '{query}'")
            return None
    except Exception as e:
        logger.error(f"Error al buscar en YouTube: {e}")
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
        # Eliminar la extensión .mp3 si ya está en el nombre
        if safe_name.lower().endswith('.mp3'):
            safe_name = safe_name[:-4]
        
        # Normalizar la ruta (convertir todas las barras a formato del sistema)
        output_path = os.path.normpath(output_path)
        output_file = os.path.normpath(os.path.join(output_path, f"{safe_name}.mp3"))
        
        logger.info(f"Descargando audio de: {video_url}")
        logger.info(f"Destino normalizado: {output_file}")
        
        # Verificar que el directorio de salida existe
        if not os.path.exists(output_path):
            logger.info(f"Creando directorio de salida: {output_path}")
            os.makedirs(output_path, exist_ok=True)
        
        # Eliminar el archivo si ya existe
        if os.path.exists(output_file):
            logger.info(f"Eliminando archivo existente: {output_file}")
            os.remove(output_file)
            
        # También verificar y eliminar si existe con doble extensión
        double_ext_file = f"{output_file}.mp3"
        if os.path.exists(double_ext_file):
            logger.info(f"Eliminando archivo con doble extensión: {double_ext_file}")
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
            logger.info("Iniciando descarga con yt-dlp...")
            ydl.download([video_url])
            logger.info("Descarga con yt-dlp finalizada")
        
        # Esperar un momento para que el sistema de archivos se actualice
        time.sleep(2)
        
        # Verificar archivos y corregir extensiones
        if os.path.exists(output_file):
            logger.info(f"Archivo encontrado correctamente: {output_file}")
        elif os.path.exists(double_ext_file):
            logger.info(f"Encontrado archivo con doble extensión: {double_ext_file}")
            logger.info(f"Renombrando a: {output_file}")
            os.rename(double_ext_file, output_file)
        else:
            # Buscar cualquier archivo que comience con el nombre base
            base_dir = os.path.dirname(output_file)
            base_name = os.path.splitext(os.path.basename(output_file))[0]
            
            logger.info(f"Buscando archivos que comiencen con: {base_name}")
            potential_files = [f for f in os.listdir(base_dir) if f.startswith(base_name)]
            
            if potential_files:
                found_file = os.path.join(base_dir, potential_files[0])
                logger.info(f"Archivo encontrado: {found_file}")
                
                if found_file != output_file:
                    logger.info(f"Renombrando {found_file} a {output_file}")
                    # Si el archivo de destino ya existe, eliminarlo primero
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    os.rename(found_file, output_file)
            else:
                logger.error(f"No se encuentra el archivo descargado")
                logger.info(f"Contenido del directorio: {os.listdir(base_dir)}")
                return False
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(output_file) / (1024*1024)
        logger.info(f"Tamaño del archivo final: {file_size:.2f} MB")
        
        if file_size < 0.1:
            logger.warning(f"¡Advertencia! El archivo es muy pequeño ({file_size:.2f} MB)")
            return False
        
        # Intentar reparar el archivo MP3 si es necesario
        fix_mp3_file(output_file)
        
        # Añadir metadatos al archivo MP3
        logger.info("Añadiendo metadatos al archivo MP3")
        metadata = get_basic_metadata(filename, cover_url, album_name)
        
        # Esperar un momento para asegurarse de que el archivo está disponible
        time.sleep(1)
        
        success = add_metadata_to_file(output_file, metadata)
        if success:
            logger.info("Metadatos añadidos correctamente")
        else:
            logger.warning("Posible problema al añadir metadatos")
        
        return True
    except Exception as e:
        logger.error(f"Error al descargar audio: {e}", exc_info=True)
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
    logger.info(f"Iniciando descarga de {len(tracks)} pistas a {destino}")
    if cover_url:
        logger.info(f"Cover URL: {cover_url}")
    if album_name:
        logger.info(f"Álbum: {album_name}")
    
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
            logger.error(f"Error en descarga: {e}")
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