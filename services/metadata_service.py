#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Servicio de metadatos para archivos de audio
"""
import os
import requests
import logging
from io import BytesIO
from PIL import Image
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TRCK, TCON
from mutagen.mp3 import MP3
from mutagen.id3._util import ID3NoHeaderError

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('metadata_service')

def add_metadata_to_file(file_path, metadata):
    """
    Añade metadatos a un archivo MP3
    
    Args:
        file_path (str): Ruta al archivo MP3
        metadata (dict): Diccionario con los metadatos a añadir
            title: Título de la canción
            artist: Artista
            album: Nombre del álbum
            year: Año de lanzamiento
            track_number: Número de pista
            genre: Género musical
            cover_url: URL de la portada
    
    Returns:
        bool: True si se añadieron los metadatos correctamente, False en caso contrario
    """
    try:
        logger.info(f"Añadiendo metadatos a: {file_path}")
        logger.info(f"Metadatos a añadir: {metadata}")
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            logger.error(f"El archivo {file_path} no existe")
            return False
        
        # Intenta abrir el archivo MP3 existente o crea uno nuevo
        try:
            audio = ID3(file_path)
            logger.info("Etiqueta ID3 existente encontrada")
        except ID3NoHeaderError:
            # Si el archivo no tiene una etiqueta ID3, la crea
            logger.info("No se encontró etiqueta ID3, creando una nueva")
            audio = ID3()
        
        # Añadir título
        if 'title' in metadata and metadata['title']:
            logger.info(f"Añadiendo título: {metadata['title']}")
            audio['TIT2'] = TIT2(encoding=3, text=metadata['title'])
        
        # Añadir artista
        if 'artist' in metadata and metadata['artist']:
            logger.info(f"Añadiendo artista: {metadata['artist']}")
            audio['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
        
        # Añadir álbum
        if 'album' in metadata and metadata['album']:
            logger.info(f"Añadiendo álbum: {metadata['album']}")
            audio['TALB'] = TALB(encoding=3, text=metadata['album'])
        
        # Añadir año
        if 'year' in metadata and metadata['year']:
            logger.info(f"Añadiendo año: {metadata['year']}")
            audio['TDRC'] = TDRC(encoding=3, text=metadata['year'])
        
        # Añadir número de pista
        if 'track_number' in metadata and metadata['track_number']:
            logger.info(f"Añadiendo número de pista: {metadata['track_number']}")
            audio['TRCK'] = TRCK(encoding=3, text=metadata['track_number'])
        
        # Añadir género
        if 'genre' in metadata and metadata['genre']:
            logger.info(f"Añadiendo género: {metadata['genre']}")
            audio['TCON'] = TCON(encoding=3, text=metadata['genre'])
        
        # Añadir portada
        if 'cover_url' in metadata and metadata['cover_url']:
            try:
                logger.info(f"Descargando portada desde: {metadata['cover_url']}")
                response = requests.get(metadata['cover_url'])
                cover_data = response.content
                
                # Procesar la imagen con PIL para asegurar compatibilidad
                try:
                    img = Image.open(BytesIO(cover_data))
                    
                    # Redimensionar si es demasiado grande (max 500x500)
                    if img.width > 500 or img.height > 500:
                        logger.info(f"Redimensionando imagen de {img.width}x{img.height} a tamaño máximo 500x500")
                        img.thumbnail((500, 500), Image.LANCZOS)
                    
                    # Convertir a formato JPEG para mayor compatibilidad
                    if img.format != 'JPEG':
                        logger.info(f"Convirtiendo imagen de formato {img.format} a JPEG")
                    
                    # Guardar en memoria
                    output = BytesIO()
                    img.convert('RGB').save(output, format='JPEG', quality=90)
                    cover_data = output.getvalue()
                    cover_type = 'image/jpeg'
                    
                    logger.info(f"Imagen procesada correctamente: {len(cover_data)} bytes, {cover_type}")
                except Exception as e:
                    logger.warning(f"Error al procesar imagen con PIL: {e}. Usando datos originales.")
                    cover_type = response.headers.get('Content-Type', 'image/jpeg')
                
                logger.info(f"Añadiendo portada, tamaño: {len(cover_data)} bytes, tipo: {cover_type}")
                
                # Eliminar portadas existentes
                for key in list(audio.keys()):
                    if key.startswith('APIC'):
                        logger.info(f"Eliminando portada existente: {key}")
                        del audio[key]
                
                # Añadir nueva portada
                audio['APIC'] = APIC(
                    encoding=3,            # 3 es para codificación UTF-8
                    mime=cover_type,       # El tipo MIME de la imagen
                    type=3,                # 3 es para la portada del álbum (front cover)
                    desc='Cover',          # Descripción
                    data=cover_data        # Los datos binarios de la imagen
                )
            except Exception as e:
                logger.error(f"Error al descargar o procesar la portada: {e}")
        
        # Guardar cambios
        logger.info(f"Guardando cambios en: {file_path}")
        audio.save(file_path, v2_version=3)  # Forzar ID3v2.3 para mayor compatibilidad
        
        # Verificar que se guardaron los metadatos
        try:
            verify_audio = ID3(file_path)
            logger.info(f"Verificación: se encontraron {len(verify_audio)} etiquetas ID3")
            for key in verify_audio.keys():
                logger.info(f"Etiqueta encontrada: {key}")
            return True
        except Exception as e:
            logger.error(f"Error al verificar metadatos: {e}")
            return False
    
    except Exception as e:
        logger.error(f"Error al añadir metadatos: {e}")
        return False

def fix_mp3_file(file_path):
    """
    Intenta reparar el archivo MP3 si no tiene etiquetas ID3 válidas
    
    Args:
        file_path (str): Ruta al archivo MP3
    
    Returns:
        bool: True si se pudo reparar, False en caso contrario
    """
    try:
        logger.info(f"Intentando reparar archivo MP3: {file_path}")
        
        # Verificar si el archivo tiene etiquetas ID3 válidas
        try:
            mp3 = MP3(file_path)
            if not mp3.tags:
                logger.info("No se encontraron etiquetas, creando nuevas")
                mp3.add_tags()
                mp3.save()
            return True
        except Exception as e:
            logger.error(f"Error al reparar MP3: {e}")
            return False
    
    except Exception as e:
        logger.error(f"Error general al reparar MP3: {e}")
        return False

def extract_metadata_from_spotify_track(track_info):
    """
    Extrae metadatos de un objeto de pista de Spotify
    
    Args:
        track_info (dict): Información de la pista de Spotify
    
    Returns:
        dict: Diccionario con los metadatos formateados
    """
    metadata = {}
    
    try:
        if 'name' in track_info:
            metadata['title'] = track_info['name']
        
        if 'artists' in track_info and track_info['artists']:
            metadata['artist'] = ', '.join([artist['name'] for artist in track_info['artists']])
        
        if 'album' in track_info and 'name' in track_info['album']:
            metadata['album'] = track_info['album']['name']
        
        if 'album' in track_info and 'release_date' in track_info['album']:
            metadata['year'] = track_info['album']['release_date'].split('-')[0]
        
        if 'track_number' in track_info:
            metadata['track_number'] = str(track_info['track_number'])
        
        if 'album' in track_info and 'images' in track_info['album'] and track_info['album']['images']:
            metadata['cover_url'] = track_info['album']['images'][0]['url']
        
        logger.info(f"Metadatos extraídos de Spotify: {metadata}")
    except Exception as e:
        logger.error(f"Error al extraer metadatos de Spotify: {e}")
    
    return metadata

def parse_track_name(track_name):
    """
    Parsea el nombre de una pista para extraer título y artista
    
    Args:
        track_name (str): Nombre de la pista en formato "título - artista"
    
    Returns:
        tuple: (título, artista)
    """
    parts = track_name.split(' - ', 1)
    title = parts[0].strip() if parts else track_name
    artist = parts[1].strip() if len(parts) > 1 else ""
    
    logger.info(f"Parseando nombre de pista: '{track_name}' → Título: '{title}', Artista: '{artist}'")
    return title, artist

def get_basic_metadata(track_name, cover_url=None, album_name=None):
    """
    Obtiene metadatos básicos a partir del nombre de la pista
    
    Args:
        track_name (str): Nombre de la pista en formato "título - artista"
        cover_url (str, optional): URL de la portada
        album_name (str, optional): Nombre del álbum
    
    Returns:
        dict: Diccionario con los metadatos básicos
    """
    title, artist = parse_track_name(track_name)
    
    metadata = {
        'title': title,
        'artist': artist,
        'album': album_name if album_name else ""
    }
    
    if cover_url:
        metadata['cover_url'] = cover_url
    
    logger.info(f"Metadatos básicos generados: {metadata}")
    return metadata