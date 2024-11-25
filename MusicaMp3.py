from youtubesearchpython import VideosSearch
import yt_dlp
import os

# Función para buscar un video en YouTube
def buscar_video_youtube(query):
    videos_search = VideosSearch(query, limit=5)
    for video in videos_search.result()['result']:
        title = video['title'].lower()
        if 'vivo' not in title:
            return video['link'], video['title']
    return None, None

# Función para descargar y convertir a mp3
def youtube_download(url, nombre):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'musica_descargada/{nombre}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': 'C:/ffmpeg',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"Descarga y conversión completa: {nombre}.mp3")

    except Exception as e:
        print(f"Error al descargar {nombre}: {e}")

# Función principal para procesar la lista de canciones
def descargar_lista_canciones(ruta_archivo_txt):
    with open(ruta_archivo_txt, 'r', encoding='utf-8') as file:
        canciones = file.readlines()

    for cancion in canciones:
        cancion = cancion.strip()
        print(f"Buscando: {cancion}")
        link, titulo = buscar_video_youtube(cancion)
        if link:
            print(f"Descargando: {titulo} desde {link}")
            youtube_download(link, titulo)
        else:
            print(f"No se encontró una versión adecuada de: {cancion}")

# Ruta del archivo de canciones
ruta_archivo_txt = 'lista_canciones.txt'

# Crear carpeta de salida si no existe
if not os.path.exists('musica_descargada'):
    os.makedirs('musica_descargada')

# Ejecutar la función principal
descargar_lista_canciones(ruta_archivo_txt)
