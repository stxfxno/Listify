#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Componentes reutilizables de UI
"""
import tkinter as tk
from config import SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY

def create_button(parent, text, command, is_primary=False, **kwargs):
    """
    Crea un botón estilizado para Listify
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar
        is_primary: Si es un botón primario (verde) o secundario (gris)
        **kwargs: Argumentos adicionales para el botón
    
    Returns:
        tk.Button: Botón estilizado
    """
    btn_color = SPOTIFY_GREEN if is_primary else SPOTIFY_DARK_GRAY
    btn_font = kwargs.pop('font', ("Helvetica", 10, "bold" if is_primary else "normal"))
    
    btn = tk.Button(
        parent,
        text=text,
        font=btn_font,
        bg=btn_color,
        fg="white",
        padx=kwargs.pop('padx', 10),
        pady=kwargs.pop('pady', 5),
        borderwidth=0,
        command=command,
        **kwargs
    )
    
    return btn

def create_label(parent, text, is_title=False, **kwargs):
    """
    Crea una etiqueta estilizada para Listify
    
    Args:
        parent: Widget padre
        text: Texto de la etiqueta
        is_title: Si es un título (más grande y en blanco) o texto normal (gris claro)
        **kwargs: Argumentos adicionales para la etiqueta
    
    Returns:
        tk.Label: Etiqueta estilizada
    """
    text_color = "white" if is_title else SPOTIFY_LIGHT_GRAY
    font_size = 16 if is_title else 10
    font_weight = "bold" if is_title else "normal"
    
    label = tk.Label(
        parent,
        text=text,
        fg=text_color,
        bg=SPOTIFY_BLACK,
        font=kwargs.pop('font', ("Helvetica", font_size, font_weight)),
        **kwargs
    )
    
    return label

def create_entry(parent, **kwargs):
    """
    Crea un campo de entrada estilizado para Listify
    
    Args:
        parent: Widget padre
        **kwargs: Argumentos adicionales para el campo de entrada
    
    Returns:
        tk.Entry: Campo de entrada estilizado
    """
    entry = tk.Entry(
        parent,
        bg=SPOTIFY_DARK_GRAY,
        fg="white",
        insertbackground="white",
        font=kwargs.pop('font', ("Helvetica", 12)),
        **kwargs
    )
    
    return entry

def create_listbox(parent, **kwargs):
    """
    Crea una lista estilizada para Listify
    
    Args:
        parent: Widget padre
        **kwargs: Argumentos adicionales para la lista
    
    Returns:
        tk.Listbox: Lista estilizada
    """
    listbox = tk.Listbox(
        parent,
        bg=SPOTIFY_DARK_GRAY,
        fg="white",
        selectbackground=SPOTIFY_GREEN,
        activestyle='none',
        font=kwargs.pop('font', ("Helvetica", 10)),
        **kwargs
    )
    
    return listbox