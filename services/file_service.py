#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Servicio de archivos
"""
import os
import re

def sanitize_filename(filename):
    """
    Sanitiza un nombre de archivo para que sea válido
    
    Args:
        filename (str): Nombre de archivo original
    
    Returns:
        str: Nombre de archivo sanitizado
    """
    # Eliminar caracteres no permitidos
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    # Acortar nombres muy largos (máximo 200 caracteres)
    if len(sanitized) > 200:
        name_parts = sanitized.split('.')
        extension = name_parts[-1] if len(name_parts) > 1 else ''
        basename = '.'.join(name_parts[:-1]) if len(name_parts) > 1 else sanitized
        
        # Truncar el nombre base y agregar la extensión
        basename = basename[:196 - len(extension)]
        sanitized = f"{basename}.{extension}" if extension else basename
    
    return sanitized

def ensure_directory_exists(directory_path):
    """
    Asegura que un directorio exista, creándolo si es necesario
    
    Args:
        directory_path (str): Ruta del directorio
    
    Returns:
        bool: True si el directorio existe o se creó correctamente
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            return True
        except Exception as e:
            print(f"Error al crear directorio: {e}")
            return False
    return True

def get_unique_filename(directory, filename):
    """
    Obtiene un nombre de archivo único para evitar sobrescrituras
    
    Args:
        directory (str): Directorio donde se guardará el archivo
        filename (str): Nombre de archivo deseado
    
    Returns:
        str: Nombre de archivo único
    """
    base_path = os.path.join(directory, filename)
    
    # Si el archivo no existe, devolver el nombre original
    if not os.path.exists(base_path):
        return filename
    
    # Si existe, añadir un contador
    name_parts = filename.split('.')
    extension = name_parts[-1] if len(name_parts) > 1 else ''
    basename = '.'.join(name_parts[:-1]) if len(name_parts) > 1 else filename
    
    counter = 1
    while True:
        if extension:
            new_filename = f"{basename} ({counter}).{extension}"
        else:
            new_filename = f"{basename} ({counter})"
        
        new_path = os.path.join(directory, new_filename)
        if not os.path.exists(new_path):
            return new_filename
        
        counter += 1