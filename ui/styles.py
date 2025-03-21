#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Estilos y temas
"""
import tkinter as tk
from tkinter import ttk
from config import SPOTIFY_GREEN, SPOTIFY_DARK_GRAY

def setup_styles(main_screen, splash_screen):
    """Configurar estilos para todos los widgets"""
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
    
    # Configurar hover para botones de la pantalla principal
    _configure_hover_buttons(main_screen)
    
    # Configurar hover para botones de la pantalla de inicio
    _configure_hover_buttons(splash_screen)

def _configure_hover_buttons(screen):
    """Configura efectos hover para los botones"""
    buttons = []
    
    # Identificar los botones en la pantalla principal
    if hasattr(screen, 'nav_btn'):
        buttons.append(screen.nav_btn)
    if hasattr(screen, 'fetch_btn'):
        buttons.append(screen.fetch_btn)
    if hasattr(screen, 'search_btn'):
        buttons.append(screen.search_btn)
    if hasattr(screen, 'folder_btn'):
        buttons.append(screen.folder_btn)
    if hasattr(screen, 'download_song_btn'):
        buttons.append(screen.download_song_btn)
    if hasattr(screen, 'download_playlist_btn'):
        buttons.append(screen.download_playlist_btn)
    if hasattr(screen, 'social_btn'):
        buttons.append(screen.social_btn)
    
    # Identificar los botones en la pantalla de inicio
    if hasattr(screen, 'inicio_btn'):
        buttons.append(screen.inicio_btn)
    if hasattr(screen, 'redes_btn'):
        buttons.append(screen.redes_btn)
    
    # Aplicar efectos hover a los botones encontrados
    for btn in buttons:
        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)

def _on_enter(e):
    """Efecto al pasar el mouse sobre un botón"""
    if e.widget['bg'] == SPOTIFY_GREEN:
        e.widget['bg'] = "#1ED760"  # Verde más claro
    else:
        e.widget['bg'] = "#444444"  # Gris más claro

def _on_leave(e):
    """Efecto al quitar el mouse de un botón"""
    if "#1ED760" in e.widget['bg']:
        e.widget['bg'] = SPOTIFY_GREEN
    else:
        e.widget['bg'] = SPOTIFY_DARK_GRAY