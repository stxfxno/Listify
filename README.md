# Listify

![Listify Logo](https://www.freepnglogos.com/uploads/spotify-logo-png/file-spotify-logo-png-4.png)

## Descripción

Listify surgió para solucionar un problema común: descargar música para eventos donde no hay conexión a internet. La aplicación te permite buscar canciones por nombre o artista, explorar playlists de Spotify, y descargar los archivos MP3 para su uso offline.

## Características

- **Búsqueda de música**: Busca canciones, artistas o álbumes directamente desde Spotify.
- **Exploración de listas**: Importa playlists completas desde Spotify con solo la URL.
- **Descarga de alta calidad**: Descarga audio en formato MP3 de alta calidad (320kbps).
- **Metadatos completos**: Incluye automáticamente título, artista, álbum y portada.
- **Interfaz intuitiva**: Diseño inspirado en Spotify para una experiencia familiar.
- **Modo pantalla completa**: Visualiza mejor las listas de reproducción extensas.

## Cómo usar

1. **Buscar canciones**:
   - Introduce el nombre de una canción o artista en el campo de búsqueda.
   - Selecciona el tipo de búsqueda (Canciones, Artistas, Álbumes).
   - Haz clic en "Buscar" para ver los resultados.

2. **Importar playlist**:
   - Copia la URL de una playlist o álbum de Spotify.
   - Pégala en el campo de URL y haz clic en "Buscar".
   - Se cargarán todas las canciones de la playlist.

3. **Descargar música**:
   - Selecciona una carpeta de destino.
   - Para descargar una sola canción, selecciónala y haz clic en "Descargar canción".
   - Para descargar toda la lista, haz clic en "Descargar playlist".

## Requisitos

- Python 3.8 o superior
- Dependencias:
  - tkinter
  - spotipy
  - yt-dlp
  - mutagen
  - pillow
  - requests
  - python-dotenv

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/listify.git
   cd listify
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura tus credenciales de Spotify:
   - Copia el archivo `.env.example` a `.env`
   - Regístrate en [Spotify Developer](https://developer.spotify.com/dashboard/) y crea una aplicación
   - Añade tu CLIENT_ID y CLIENT_SECRET en el archivo `.env`

4. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar Listify, por favor:

1. Haz fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Contacto

- **Desarrollador**: [Stef.dev](https://www.instagram.com/stef.dev_/)
- **GitHub**: [github.com/stefdev_](https://github.com/stefdev_)
- **Twitter**: [@stefdev_](https://twitter.com/stefdev_)
- **LinkedIn**: [linkedin.com/in/stefdev](https://linkedin.com/in/stefdev)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Aviso legal

Esta aplicación está diseñada para uso personal y educativo. No promocionamos la piratería ni la distribución ilegal de contenido protegido por derechos de autor. Por favor utiliza esta herramienta de forma responsable y respeta las leyes de propiedad intelectual de tu país.