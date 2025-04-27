#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Servicio de reproductor de música
"""
import os
import pygame
import threading
import time
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from PIL import Image, ImageTk
from io import BytesIO

class MusicPlayerService:
    """Clase para gestionar la reproducción de música"""
    def __init__(self):
        # Inicializar pygame mixer para reproducción de audio
        pygame.mixer.init()
        
        # Variables de control
        self.current_song = None
        self.paused = False
        self.stopped = True
        self.volume = 0.5  # Volumen por defecto (0.0 a 1.0)
        
        # Estado de reproducción
        self.current_time = 0
        self.song_length = 0
        self.update_thread = None
        self.thread_running = False
        
        # Lista de canciones
        self.playlist = []
        self.current_index = -1
    
    def set_volume(self, volume):
        """
        Establece el volumen de reproducción
        
        Args:
            volume (float): Nivel de volumen entre 0.0 y 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def scan_directory(self, directory):
        """
        Escanea un directorio en busca de archivos MP3
        
        Args:
            directory (str): Ruta del directorio a escanear
        
        Returns:
            list: Lista de rutas a archivos MP3
        """
        mp3_files = []
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        full_path = os.path.join(root, file)
                        mp3_files.append(full_path)
        except Exception as e:
            print(f"Error al escanear directorio: {e}")
        
        return sorted(mp3_files)
    
    def load_playlist(self, mp3_files):
        """
        Carga una lista de archivos MP3 como playlist
        
        Args:
            mp3_files (list): Lista de rutas a archivos MP3
        """
        self.playlist = mp3_files
        self.current_index = -1
    
    def play(self, song_path=None, index=None):
        """
        Reproduce una canción
        
        Args:
            song_path (str, optional): Ruta del archivo MP3 a reproducir
            index (int, optional): Índice de la canción en la playlist
        
        Returns:
            dict: Metadatos de la canción o None si hay error
        """
        # Determinar qué canción reproducir
        if index is not None and 0 <= index < len(self.playlist):
            song_path = self.playlist[index]
            self.current_index = index
        elif song_path:
            # Buscar el índice de la canción en la playlist
            try:
                self.current_index = self.playlist.index(song_path)
            except ValueError:
                self.current_index = -1
        elif self.current_index >= 0:
            # Continuar con la canción actual
            song_path = self.playlist[self.current_index]
        else:
            # No hay canción para reproducir
            return None
        
        try:
            # Detener la reproducción actual
            self.stop()
            
            # Cargar y reproducir la nueva canción
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            # Actualizar estado
            self.current_song = song_path
            self.paused = False
            self.stopped = False
            
            # Obtener duración
            audio = MP3(song_path)
            self.song_length = audio.info.length
            
            # Iniciar hilo de actualización
            self.start_update_thread()
            
            # Obtener metadatos
            return self.get_song_metadata(song_path)
        
        except Exception as e:
            print(f"Error al reproducir canción: {e}")
            return None
    
    def pause(self):
        """Pausa la reproducción actual"""
        if not self.stopped and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
    
    def resume(self):
        """Reanuda la reproducción pausada"""
        if not self.stopped and self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
    
    def stop(self):
        """Detiene la reproducción actual"""
        if not self.stopped:
            pygame.mixer.music.stop()
            self.stopped = True
            self.paused = False
            self.thread_running = False
            
            # Esperar a que el hilo de actualización termine
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join()
    
    def play_next(self):
        """
        Reproduce la siguiente canción en la playlist
        
        Returns:
            dict: Metadatos de la canción o None si no hay siguiente
        """
        if not self.playlist:
            return None
        
        next_index = (self.current_index + 1) % len(self.playlist)
        return self.play(index=next_index)
    
    def play_previous(self):
        """
        Reproduce la canción anterior en la playlist
        
        Returns:
            dict: Metadatos de la canción o None si no hay anterior
        """
        if not self.playlist:
            return None
        
        prev_index = (self.current_index - 1) % len(self.playlist)
        return self.play(index=prev_index)
    
    def get_song_metadata(self, song_path):
        """
        Obtiene los metadatos de una canción
        
        Args:
            song_path (str): Ruta del archivo MP3
        
        Returns:
            dict: Metadatos de la canción
        """
        metadata = {
            'title': os.path.splitext(os.path.basename(song_path))[0],
            'artist': 'Desconocido',
            'album': 'Desconocido',
            'cover': None,
            'path': song_path
        }
        
        try:
            audio = ID3(song_path)
            
            # Obtener título
            if 'TIT2' in audio:
                metadata['title'] = audio['TIT2'].text[0]
            
            # Obtener artista
            if 'TPE1' in audio:
                metadata['artist'] = audio['TPE1'].text[0]
            
            # Obtener álbum
            if 'TALB' in audio:
                metadata['album'] = audio['TALB'].text[0]
            
            # Obtener portada
            if 'APIC:' in audio or 'APIC:Cover' in audio:
                apic_key = 'APIC:' if 'APIC:' in audio else 'APIC:Cover'
                cover_data = audio[apic_key].data
                metadata['cover'] = cover_data
        
        except Exception as e:
            print(f"Error al obtener metadatos: {e}")
        
        return metadata
    
    def seek(self, position):
        """
        Busca una posición específica en la canción
        
        Args:
            position (float): Posición en segundos
        """
        if not self.stopped:
            # Asegurar que la posición esté dentro de los límites
            position = max(0, min(position, self.song_length))
            
            # Establecer la posición
            pygame.mixer.music.set_pos(position)
            self.current_time = position
    
    def seek_percentage(self, percentage):
        """
        Busca una posición específica en la canción por porcentaje
        
        Args:
            percentage (float): Porcentaje de la canción (0.0 a 1.0)
        """
        if not self.stopped and self.song_length > 0:
            new_position = self.song_length * percentage
            self.seek(new_position)
    
    def get_position(self):
        """
        Obtiene la posición actual de reproducción
        
        Returns:
            float: Posición actual en segundos
        """
        return self.current_time
    
    def get_length(self):
        """
        Obtiene la duración total de la canción actual
        
        Returns:
            float: Duración en segundos
        """
        return self.song_length
    
    def is_playing(self):
        """
        Verifica si hay música reproduciéndose
        
        Returns:
            bool: True si se está reproduciendo música, False en caso contrario
        """
        return not self.stopped and not self.paused
    
    def is_paused(self):
        """
        Verifica si la reproducción está pausada
        
        Returns:
            bool: True si la reproducción está pausada, False en caso contrario
        """
        return self.paused
    
    def start_update_thread(self):
        """Inicia un hilo para actualizar la posición actual"""
        self.thread_running = True
        self.update_thread = threading.Thread(target=self._update_position, daemon=True)
        self.update_thread.start()
    
    def _update_position(self):
        """Actualiza la posición actual periódicamente"""
        self.current_time = 0
        
        while self.thread_running and not self.stopped:
            if not self.paused and pygame.mixer.music.get_busy():
                # Actualizar tiempo (pygame no proporciona la posición exacta, así que la estimamos)
                time.sleep(0.1)
                self.current_time = min(self.current_time + 0.1, self.song_length)
                
                # Verificar si la canción ha terminado
                if self.current_time >= self.song_length:
                    self.thread_running = False
                    # Programar la reproducción de la siguiente canción
                    threading.Thread(target=self.play_next, daemon=True).start()
            else:
                time.sleep(0.1)
    
    def cleanup(self):
        """Limpia los recursos cuando se cierra la app"""
        self.stop()
        pygame.mixer.quit()