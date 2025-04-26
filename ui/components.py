#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Componentes reutilizables de UI modernizados
"""
import tkinter as tk
from config import SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_DARK_GRAY, SPOTIFY_LIGHT_GRAY

# Colores adicionales para componentes más atractivos
SPOTIFY_HOVER_GREEN = "#1ED760"
SPOTIFY_HOVER_GRAY = "#444444"
SPOTIFY_LIGHTER_GRAY = "#CCCCCC"
SPOTIFY_SOFT_BLACK = "#121212"

def create_button(parent, text, command, is_primary=False, **kwargs):
    """
    Crea un botón estilizado para Listify con diseño moderno
    
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
    btn_font = kwargs.pop('font', ("Helvetica", 11, "bold" if is_primary else "normal"))
    
    # Valores por defecto mejorados
    padx_value = kwargs.pop('padx', 15)
    pady_value = kwargs.pop('pady', 8)
    
    btn = tk.Button(
        parent,
        text=text,
        font=btn_font,
        bg=btn_color,
        fg="white",
        padx=padx_value,
        pady=pady_value,
        borderwidth=0,
        highlightthickness=0,
        activebackground=SPOTIFY_HOVER_GREEN if is_primary else SPOTIFY_HOVER_GRAY,
        activeforeground="white",
        relief="flat",
        command=command,
        **kwargs
    )
    
    # Guardar si es un botón primario como atributo
    btn.primary = is_primary
    
    # Agregar efectos hover
    btn.bind("<Enter>", lambda e: _on_button_enter(e, is_primary))
    btn.bind("<Leave>", lambda e: _on_button_leave(e, is_primary))
    
    # Agregar efectos de pulsación
    btn.bind("<ButtonPress-1>", _on_button_press)
    btn.bind("<ButtonRelease-1>", _on_button_release)
    
    return btn

def create_label(parent, text, is_title=False, **kwargs):
    """
    Crea una etiqueta estilizada para Listify con diseño mejorado
    
    Args:
        parent: Widget padre
        text: Texto de la etiqueta
        is_title: Si es un título (más grande y en blanco) o texto normal (gris claro)
        **kwargs: Argumentos adicionales para la etiqueta
    
    Returns:
        tk.Label: Etiqueta estilizada
    """
    text_color = "white" if is_title else SPOTIFY_LIGHT_GRAY
    font_size = 18 if is_title else 11
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
    Crea un campo de entrada estilizado para Listify con diseño moderno
    
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
        insertbackground=SPOTIFY_GREEN,  # Cursor color mejorado
        insertwidth=3,                   # Cursor más visible
        font=kwargs.pop('font', ("Helvetica", 12)),
        borderwidth=0,                   # Sin borde
        highlightthickness=1,            # Resaltado más sutil
        highlightbackground=SPOTIFY_DARK_GRAY,
        highlightcolor=SPOTIFY_GREEN,    # Resaltado en verde al tener foco
        relief="flat",                   # Aspecto plano moderno
        bd=0,                            # Sin borde adicional
        **kwargs
    )
    
    # Nota: Los widgets Entry en Tkinter no soportan padx/pady directamente
    
    # Agregar efectos hover
    entry.bind("<FocusIn>", _on_entry_focus_in)
    entry.bind("<FocusOut>", _on_entry_focus_out)
    
    return entry

def create_listbox(parent, **kwargs):
    """
    Crea una lista estilizada para Listify con diseño moderno
    
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
        selectforeground="white",
        activestyle='none',
        font=kwargs.pop('font', ("Helvetica", 11)),
        borderwidth=0,               # Sin borde
        highlightthickness=1,        # Resaltado sutil
        highlightbackground=SPOTIFY_DARK_GRAY,
        highlightcolor=SPOTIFY_GREEN,  # Resaltado en verde al tener foco
        relief="flat",               # Aspecto plano moderno
        selectborderwidth=0,         # Sin borde en selección
        exportselection=False,       # Mantener selección al perder foco
        **kwargs
    )
    
    return listbox

def create_frame(parent, has_border=False, **kwargs):
    """
    Crea un frame estilizado para Listify
    
    Args:
        parent: Widget padre
        has_border: Si debe tener un borde sutil
        **kwargs: Argumentos adicionales para el frame
    
    Returns:
        tk.Frame: Frame estilizado
    """
    highlight_thickness = 1 if has_border else 0
    highlight_bg = SPOTIFY_DARK_GRAY if has_border else SPOTIFY_BLACK
    
    frame = tk.Frame(
        parent,
        bg=SPOTIFY_BLACK,
        highlightthickness=highlight_thickness, 
        highlightbackground=highlight_bg,
        bd=0,
        relief="flat",
        **kwargs
    )
    
    return frame

def create_scrolled_frame(parent, **kwargs):
    """
    Crea un frame con scrollbar para contenido extenso
    
    Args:
        parent: Widget padre
        **kwargs: Argumentos adicionales para el frame
    
    Returns:
        tuple: (frame_exterior, frame_interior)
    """
    from tkinter import ttk
    
    # Frame exterior que contiene todo
    exterior = tk.Frame(parent, bg=SPOTIFY_BLACK, **kwargs)
    
    # Canvas para el scroll
    canvas = tk.Canvas(
        exterior, 
        bg=SPOTIFY_BLACK, 
        bd=0, 
        highlightthickness=0,
        relief='flat'
    )
    scrollbar = ttk.Scrollbar(
        exterior, 
        orient="vertical", 
        command=canvas.yview,
        style="Vertical.TScrollbar"
    )
    
    # Frame interior que contiene el contenido
    interior = tk.Frame(canvas, bg=SPOTIFY_BLACK)
    
    # Configuración
    interior.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=interior, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Empaquetar todo
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Agregar scrolling con rueda de mouse
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    return exterior, interior

# Funciones de efecto para botones
def _on_button_enter(e, is_primary):
    """Efecto al pasar el mouse sobre un botón"""
    e.widget.config(
        bg=SPOTIFY_HOVER_GREEN if is_primary else SPOTIFY_HOVER_GRAY,
        cursor="hand2"
    )

def _on_button_leave(e, is_primary):
    """Efecto al quitar el mouse de un botón"""
    e.widget.config(
        bg=SPOTIFY_GREEN if is_primary else SPOTIFY_DARK_GRAY
    )

def _on_button_press(e):
    """Efecto al presionar el botón"""
    # Reducir ligeramente el tamaño para efecto de pulsación
    current_padx = e.widget['padx']
    current_pady = e.widget['pady']
    e.widget.config(padx=int(current_padx)-1, pady=int(current_pady)-1)

def _on_button_release(e):
    """Efecto al soltar el botón"""
    # Restaurar el tamaño original
    current_padx = e.widget['padx'] 
    current_pady = e.widget['pady']
    e.widget.config(padx=int(current_padx)+1, pady=int(current_pady)+1)

# Funciones de efecto para campos de entrada
def _on_entry_focus_in(e):
    """Efecto al recibir foco en entrada"""
    e.widget.config(highlightbackground=SPOTIFY_GREEN)

def _on_entry_focus_out(e):
    """Efecto al perder foco en entrada"""
    e.widget.config(highlightbackground=SPOTIFY_DARK_GRAY)