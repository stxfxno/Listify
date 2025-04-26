#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Estilos y temas
"""
import tkinter as tk
from tkinter import ttk
from config import SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY

# Colores adicionales para una interfaz más rica
SPOTIFY_HOVER_GREEN = "#1ED760"
SPOTIFY_HOVER_GRAY = "#444444"

def setup_styles(main_screen, splash_screen):
    """Configurar estilos para todos los widgets con una apariencia más moderna"""
    # Configurar estilos para ttk widgets
    style = ttk.Style()
    style.theme_use('default')
    
    # Barra de progreso mejorada
    style.configure("TProgressbar", 
                thickness=8, 
                troughcolor=SPOTIFY_BLACK,
                background=SPOTIFY_GREEN,
                borderwidth=0,
                relief="flat")
    
    # Combobox mejorado
    style.configure("TCombobox", 
                fieldbackground=SPOTIFY_DARK_GRAY,
                background=SPOTIFY_DARK_GRAY,
                foreground="white",
                selectbackground=SPOTIFY_GREEN,
                arrowcolor="white")
    
    style.map("TCombobox",
            fieldbackground=[('readonly', SPOTIFY_DARK_GRAY)],
            selectbackground=[('readonly', SPOTIFY_GREEN)],
            selectforeground=[('readonly', 'white')])
    
    # Configurar scrollbar personalizada
    style.configure("Vertical.TScrollbar", 
                background=SPOTIFY_DARK_GRAY, 
                troughcolor=SPOTIFY_BLACK,
                arrowcolor=SPOTIFY_LIGHT_GRAY)
    
    # Configurar hover para botones
    _configure_hover_buttons(main_screen)
    _configure_hover_buttons(splash_screen)

def _configure_hover_buttons(screen):
    """Configura efectos hover para los botones"""
    buttons = []
    
    # Identificar todos los botones en el objeto
    for attr_name in dir(screen):
        if attr_name.endswith('_btn') and hasattr(screen, attr_name):
            btn = getattr(screen, attr_name)
            if isinstance(btn, tk.Button):
                buttons.append(btn)
    
    # Aplicar efectos hover a los botones encontrados
    for btn in buttons:
        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)

def _on_enter(e):
    """Efecto al pasar el mouse sobre un botón"""
    if e.widget['bg'] == SPOTIFY_GREEN:
        e.widget.config(bg=SPOTIFY_HOVER_GREEN, cursor="hand2")
    else:
        e.widget.config(bg=SPOTIFY_HOVER_GRAY, cursor="hand2")

def _on_leave(e):
    """Efecto al quitar el mouse de un botón"""
    if SPOTIFY_HOVER_GREEN in e.widget['bg']:
        e.widget.config(bg=SPOTIFY_GREEN)
    else:
        e.widget.config(bg=SPOTIFY_DARK_GRAY)