#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herramienta para verificar metadatos de archivos MP3
"""
import os
import sys
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.id3._util import ID3NoHeaderError
import tkinter as tk
from tkinter import filedialog, ttk

def check_file_metadata(file_path):
    """
    Verifica y muestra los metadatos de un archivo MP3
    
    Args:
        file_path (str): Ruta al archivo MP3
    
    Returns:
        dict: Diccionario con los metadatos encontrados
    """
    result = {
        'file_name': os.path.basename(file_path),
        'file_size': f"{os.path.getsize(file_path) / (1024*1024):.2f} MB",
        'metadata': {}
    }
    
    try:
        # Verificar si es un archivo MP3 válido
        mp3 = MP3(file_path)
        result['duration'] = f"{mp3.info.length:.2f} segundos"
        result['bitrate'] = f"{mp3.info.bitrate / 1000:.0f} kbps"
        
        # Obtener etiquetas ID3
        try:
            id3 = ID3(file_path)
            result['id3_version'] = ".".join(str(v) for v in id3.version)
            
            # Título
            if 'TIT2' in id3:
                result['metadata']['title'] = id3['TIT2'].text[0]
            
            # Artista
            if 'TPE1' in id3:
                result['metadata']['artist'] = id3['TPE1'].text[0]
            
            # Álbum
            if 'TALB' in id3:
                result['metadata']['album'] = id3['TALB'].text[0]
            
            # Año
            if 'TDRC' in id3:
                result['metadata']['year'] = str(id3['TDRC'].text[0])
            
            # Número de pista
            if 'TRCK' in id3:
                result['metadata']['track'] = id3['TRCK'].text[0]
            
            # Género
            if 'TCON' in id3:
                result['metadata']['genre'] = id3['TCON'].text[0]
            
            # Portada
            if 'APIC:' in id3 or 'APIC:Cover' in id3:
                apic_key = 'APIC:' if 'APIC:' in id3 else 'APIC:Cover'
                result['metadata']['cover'] = f"Sí ({len(id3[apic_key].data) / 1024:.1f} KB)"
            
            # Todas las etiquetas
            result['all_tags'] = list(id3.keys())
            
        except ID3NoHeaderError:
            result['error'] = "No se encontraron etiquetas ID3"
        
    except Exception as e:
        result['error'] = f"Error al leer el archivo: {str(e)}"
    
    return result

def print_metadata(metadata):
    """Imprime los metadatos en la consola de manera legible"""
    print("\n" + "="*50)
    print(f"Archivo: {metadata['file_name']}")
    print(f"Tamaño: {metadata['file_size']}")
    
    if 'duration' in metadata:
        print(f"Duración: {metadata['duration']}")
    
    if 'bitrate' in metadata:
        print(f"Bitrate: {metadata['bitrate']}")
    
    if 'id3_version' in metadata:
        print(f"Versión ID3: {metadata['id3_version']}")
    
    print("\nMetadatos encontrados:")
    if not metadata['metadata']:
        print("  No se encontraron metadatos")
    else:
        for key, value in metadata['metadata'].items():
            print(f"  {key.capitalize()}: {value}")
    
    if 'all_tags' in metadata:
        print("\nEtiquetas ID3 disponibles:")
        print(f"  {', '.join(metadata['all_tags'])}")
    
    if 'error' in metadata:
        print(f"\nError: {metadata['error']}")
    
    print("="*50 + "\n")

class MetadataCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comprobador de Metadatos MP3")
        self.root.geometry("800x600")
        
        # Marco principal
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botón para seleccionar archivo
        self.select_btn = ttk.Button(self.main_frame, text="Seleccionar archivo MP3", command=self.select_file)
        self.select_btn.pack(pady=10)
        
        # Etiqueta para el archivo seleccionado
        self.file_label = ttk.Label(self.main_frame, text="Ningún archivo seleccionado")
        self.file_label.pack(pady=5)
        
        # Marco para la información
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Información del archivo")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.info_text = tk.Text(self.info_frame, height=5, width=80)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Marco para los metadatos
        self.metadata_frame = ttk.LabelFrame(self.main_frame, text="Metadatos")
        self.metadata_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.metadata_tree = ttk.Treeview(self.metadata_frame, columns=("value"), show="headings")
        self.metadata_tree.heading("value", text="Valor")
        self.metadata_tree.column("value", width=300)
        self.metadata_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Marco para las etiquetas ID3
        self.tags_frame = ttk.LabelFrame(self.main_frame, text="Etiquetas ID3 disponibles")
        self.tags_frame.pack(fill=tk.X, pady=10)
        
        self.tags_text = tk.Text(self.tags_frame, height=5, width=80)
        self.tags_text.pack(fill=tk.X, padx=5, pady=5)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo MP3",
            filetypes=[("Archivos MP3", "*.mp3")]
        )
        
        if file_path:
            self.file_label.config(text=file_path)
            self.check_metadata(file_path)
    
    def check_metadata(self, file_path):
        # Limpiar widgets
        self.info_text.delete(1.0, tk.END)
        self.tags_text.delete(1.0, tk.END)
        for item in self.metadata_tree.get_children():
            self.metadata_tree.delete(item)
        
        # Obtener metadatos
        metadata = check_file_metadata(file_path)
        
        # Mostrar información del archivo
        self.info_text.insert(tk.END, f"Archivo: {metadata['file_name']}\n")
        self.info_text.insert(tk.END, f"Tamaño: {metadata['file_size']}\n")
        
        if 'duration' in metadata:
            self.info_text.insert(tk.END, f"Duración: {metadata['duration']}\n")
        
        if 'bitrate' in metadata:
            self.info_text.insert(tk.END, f"Bitrate: {metadata['bitrate']}\n")
        
        if 'id3_version' in metadata:
            self.info_text.insert(tk.END, f"Versión ID3: {metadata['id3_version']}\n")
        
        # Mostrar metadatos
        if not metadata['metadata']:
            self.metadata_tree.insert("", tk.END, values=("No se encontraron metadatos", ""))
        else:
            for key, value in metadata['metadata'].items():
                self.metadata_tree.insert("", tk.END, text=key, values=(value,), iid=key)
        
        # Mostrar etiquetas ID3
        if 'all_tags' in metadata:
            self.tags_text.insert(tk.END, ", ".join(metadata['all_tags']))
        
        if 'error' in metadata:
            self.tags_text.insert(tk.END, f"Error: {metadata['error']}")

def main():
    """Función principal"""
    # Verificar si se proporciona un archivo como argumento
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path) and file_path.lower().endswith('.mp3'):
            metadata = check_file_metadata(file_path)
            print_metadata(metadata)
        else:
            print(f"Error: {file_path} no es un archivo MP3 válido")
    else:
        # Iniciar interfaz gráfica
        root = tk.Tk()
        app = MetadataCheckerGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()