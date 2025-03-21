#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Punto de entrada principal
"""
import tkinter as tk
from dotenv import load_dotenv
from ui.app import ListifyApp

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    app = ListifyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()