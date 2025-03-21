#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listify - Servicio de Spotify
"""
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tkinter import messagebox
from config import CLIENT_ID, CLIENT_SECRET

def get_spotify_client():
    """
    Obtiene un cliente de Spotify API
    
    Returns:
        spotipy.Spotify: Cliente de Spotify
    """
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, 
        client_secret=CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_spotify(query, search_type):
    """
    Busca en Spotify según el tipo de búsqueda
    
    Args:
        query (str): Término de búsqueda
        search_type (str): Tipo de búsqueda (canciones, artistas, álbumes)
    
    Returns:
        tuple: (resultados, url_portada, título)
    """
    sp = get_spotify_client()
    
    results = []
    cover_url = None
    title = f"Resultados para: {query}"
    
    try:
        if search_type == "canciones":
            spotify_type = "track"
            response = sp.search(q=query, type=spotify_type, limit=50)
            items = response['tracks']['items']
            for item in items:
                results.append(f"{item['name']} - {', '.join(artist['name'] for artist in item['artists'])}")
            if items and items[0]['album']['images']:
                cover_url = items[0]['album']['images'][0]['url']
        
        elif search_type == "artistas":
            spotify_type = "artist"
            response = sp.search(q=query, type=spotify_type, limit=20)
            items = response['artists']['items']
            for item in items:
                results.append(f"{item['name']} - Artista")
                # Obtener los top tracks del primer artista
                if items and items[0]['id'] and not results:
                    top_tracks = sp.artist_top_tracks(items[0]['id'])
                    for track in top_tracks['tracks']:
                        results.append(f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
            if items and items[0]['images']:
                cover_url = items[0]['images'][0]['url']
        
        elif search_type == "álbumes":
            spotify_type = "album"
            response = sp.search(q=query, type=spotify_type, limit=20)
            items = response['albums']['items']
            
            for album in items:
                results.append(f"ÁLBUM: {album['name']} - {', '.join(artist['name'] for artist in album['artists'])}")
                
                # Obtener las canciones del álbum
                album_tracks = sp.album_tracks(album['id'])
                for track in album_tracks['items']:
                    results.append(f"  • {track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
            
            if items and items[0]['images']:
                cover_url = items[0]['images'][0]['url']
        
        return results, cover_url, title
    
    except Exception as e:
        messagebox.showerror("Error", f"Error al buscar en Spotify: {e}")
        return [], None, f"Error en la búsqueda: {query}"

def get_tracks_from_url(url):
    """
    Obtiene las pistas desde una URL de Spotify (álbum o playlist)
    
    Args:
        url (str): URL de Spotify
    
    Returns:
        tuple: (pistas, url_portada, título)
    """
    sp = get_spotify_client()
    
    tracks = []
    cover_url = None
    title = ""
    
    try:
        if 'album' in url:
            album_id = re.search(r'album/([a-zA-Z0-9]+)', url).group(1)
            results = sp.album_tracks(album_id)
            album_info = sp.album(album_id)
            cover_url = album_info['images'][0]['url'] if album_info['images'] else None
            title = f"{album_info['name']} - {album_info['artists'][0]['name']}"
            for item in results['items']:
                tracks.append(f"{item['name']} - {', '.join(artist['name'] for artist in item['artists'])}")
        elif 'playlist' in url:
            playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url).group(1)
            results = sp.playlist_tracks(playlist_id)
            playlist_info = sp.playlist(playlist_id)
            cover_url = playlist_info['images'][0]['url'] if playlist_info['images'] else None
            title = playlist_info['name']
            while results:
                for item in results['items']:
                    track = item.get('track')
                    if track and track['type'] == 'track':
                        tracks.append(f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
                results = sp.next(results) if results['next'] else None
        else:
            messagebox.showerror("Error", "URL inválida. Debe ser un álbum o playlist de Spotify.")
            return [], None, None
        return tracks, cover_url, title
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener datos de Spotify: {e}")
        return [], None, None