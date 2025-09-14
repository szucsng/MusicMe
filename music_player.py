import discord
import asyncio
import yt_dlp
import os
import subprocess
import re
from collections import deque
from typing import Optional, Dict, List
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, COLORS

# Spotify támogatás
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False
    print("⚠️ Spotify támogatás nem elérhető. Telepítsd: pip install spotipy")

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}
        self.now_playing = {}
        
        # Spotify API inicializálása
        self.spotify = None
        if SPOTIFY_AVAILABLE and SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                print("✅ Spotify API sikeresen inicializálva!")
            except Exception as e:
                print(f"❌ Spotify API inicializálási hiba: {e}")
                self.spotify = None
        
        # yt-dlp beállítások DRM védett videók kiszűrésére
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            # DRM védett videók kiszűrése
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'live'],
                }
            }
        }
        
        # FFmpeg beállítások
        self.ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }
    
    async def check_ffmpeg(self) -> bool:
        """FFmpeg telepítés ellenőrzése"""
        try:
            # Próbáljuk meg megtalálni az FFmpeg-et
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    async def join_voice_channel(self, interaction: discord.Interaction) -> bool:
        """Csatlakozás a hangcsatornához"""
        if not interaction.user.voice:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagy hangcsatornában! Csatlakozz egy hangcsatornához először!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        voice_channel = interaction.user.voice.channel
        
        try:
            # FFmpeg ellenőrzés
            if not await self.check_ffmpeg():
                embed = discord.Embed(
                    title="❌ FFmpeg nincs telepítve!",
                    description="Az FFmpeg telepítése szükséges a zene lejátszáshoz!\n\n"
                               "**Windows:** `winget install Gyan.FFmpeg`\n"
                               "**Linux:** `sudo apt install ffmpeg`\n"
                               "**macOS:** `brew install ffmpeg`",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed)
                return False
            
            voice_client = await voice_channel.connect()
            self.voice_clients[interaction.guild.id] = voice_client
            self.queues[interaction.guild.id] = deque()
            self.now_playing[interaction.guild.id] = None
            
            embed = discord.Embed(
                title="✅ Csatlakozás!",
                description=f"Csatlakoztam a **{voice_channel.name}** hangcsatornához!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Hiba!",
                description=f"Nem sikerült csatlakozni a hangcsatornához: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    async def leave_voice_channel(self, interaction: discord.Interaction) -> bool:
        """Kilépés a hangcsatornából"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        try:
            voice_client = self.voice_clients[guild_id]
            await voice_client.disconnect()
            
            # Adatok törlése
            del self.voice_clients[guild_id]
            del self.queues[guild_id]
            del self.now_playing[guild_id]
            
            embed = discord.Embed(
                title="👋 Kilépés!",
                description="Kiléptem a hangcsatornából!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Hiba!",
                description=f"Hiba a kilépés során: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    def is_spotify_url(self, url: str) -> bool:
        """Ellenőrzi, hogy a URL Spotify link-e"""
        return 'open.spotify.com' in url or 'spotify.com' in url
    
    def is_spotify_playlist(self, url: str) -> bool:
        """Ellenőrzi, hogy a URL Spotify playlist-e"""
        return 'playlist' in url
    
    def is_spotify_album(self, url: str) -> bool:
        """Ellenőrzi, hogy a URL Spotify album-e"""
        return 'album' in url
    
    def is_spotify_track(self, url: str) -> bool:
        """Ellenőrzi, hogy a URL Spotify track-e"""
        return 'track' in url
    
    async def search_spotify(self, query: str) -> Optional[Dict]:
        """Spotify keresés"""
        if not self.spotify:
            return None
        
        try:
            # Ha URL, próbáljuk meg kivonni az információt
            if self.is_spotify_url(query):
                return await self.get_spotify_info(query)
            
            # Ha nem URL, keressük meg
            results = self.spotify.search(q=query, type='track', limit=1)
            
            if not results['tracks']['items']:
                return None
            
            track = results['tracks']['items'][0]
            
            return {
                'title': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Ismeretlen előadó',
                'album': track['album']['name'] if track['album'] else 'Ismeretlen album',
                'duration': track['duration_ms'] // 1000,  # milliszekundum -> másodperc
                'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'spotify_url': track['external_urls']['spotify'],
                'type': 'spotify_track'
            }
            
        except Exception as e:
            print(f"Hiba a Spotify keresés során: {e}")
            return None
    
    async def get_spotify_info(self, url: str) -> Optional[Dict]:
        """Spotify URL információ kinyerése"""
        if not self.spotify:
            return None
        
        try:
            if self.is_spotify_track(url):
                # Track információ
                track_id = url.split('track/')[-1].split('?')[0]
                track = self.spotify.track(track_id)
                
                return {
                    'title': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Ismeretlen előadó',
                    'album': track['album']['name'] if track['album'] else 'Ismeretlen album',
                    'duration': track['duration_ms'] // 1000,
                    'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'spotify_url': track['external_urls']['spotify'],
                    'type': 'spotify_track'
                }
            
            elif self.is_spotify_playlist(url):
                # Playlist összes számának információja
                playlist_id = url.split('playlist/')[-1].split('?')[0]
                playlist_info = self.spotify.playlist(playlist_id)
                playlist_tracks = self.spotify.playlist_tracks(playlist_id, limit=50)  # Maximum 50 szám
                
                if not playlist_tracks['items']:
                    return None
                
                tracks = []
                for item in playlist_tracks['items']:
                    if item['track']:
                        track = item['track']
                        tracks.append({
                            'title': track['name'],
                            'artist': track['artists'][0]['name'] if track['artists'] else 'Ismeretlen előadó',
                            'album': track['album']['name'] if track['album'] else 'Ismeretlen album',
                            'duration': track['duration_ms'] // 1000,
                            'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'spotify_url': track['external_urls']['spotify'],
                            'type': 'spotify_playlist_track'
                        })
                
                return {
                    'title': f"Playlist: {playlist_info['name']}",
                    'artist': f"{len(tracks)} szám",
                    'album': playlist_info.get('description', 'Nincs leírás'),
                    'duration': sum(track['duration'] for track in tracks),
                    'thumbnail': playlist_info['images'][0]['url'] if playlist_info['images'] else None,
                    'spotify_url': playlist_info['external_urls']['spotify'],
                    'type': 'spotify_playlist',
                    'tracks': tracks,
                    'playlist_name': playlist_info['name']
                }
            
            elif self.is_spotify_album(url):
                # Album összes számának információja
                album_id = url.split('album/')[-1].split('?')[0]
                album_info = self.spotify.album(album_id)
                album_tracks = self.spotify.album_tracks(album_id)
                
                if not album_tracks['items']:
                    return None
                
                tracks = []
                for track in album_tracks['items']:
                    tracks.append({
                        'title': track['name'],
                        'artist': track['artists'][0]['name'] if track['artists'] else 'Ismeretlen előadó',
                        'album': album_info['name'],
                        'duration': track['duration_ms'] // 1000,
                        'thumbnail': album_info['images'][0]['url'] if album_info['images'] else None,
                        'spotify_url': track['external_urls']['spotify'],
                        'type': 'spotify_album_track'
                    })
                
                return {
                    'title': f"Album: {album_info['name']}",
                    'artist': album_info['artists'][0]['name'] if album_info['artists'] else 'Ismeretlen előadó',
                    'album': album_info['name'],
                    'duration': sum(track['duration'] for track in tracks),
                    'thumbnail': album_info['images'][0]['url'] if album_info['images'] else None,
                    'spotify_url': album_info['external_urls']['spotify'],
                    'type': 'spotify_album',
                    'tracks': tracks,
                    'album_name': album_info['name']
                }
            
            return None
            
        except Exception as e:
            print(f"Hiba a Spotify információ kinyerése során: {e}")
            return None
    
    async def search_youtube(self, query: str) -> Optional[Dict]:
        """YouTube keresés - minden fajta zene támogatott, kivéve élő adások"""
        try:
            # Speciális yt-dlp beállítások a jobb kompatibilitáshoz
            search_opts = self.ydl_opts.copy()
            search_opts.update({
                'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '0',  # Legjobb minőség
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'auto',
                'source_address': '0.0.0.0',
                # DRM ellenőrzés eltávolítva - minden videó támogatott
                'extractor_args': {
                    'youtube': {
                        'skip': ['live'],  # Csak élő adásokat hagyunk ki
                    }
                }
            })
            
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                try:
                    # Próbáljuk meg a keresést
                    if query.startswith(('http://', 'https://')):
                        # Ha URL, közvetlenül próbáljuk meg
                        info = ydl.extract_info(query, download=False)
                        video = info
                    else:
                        # Ha keresési kifejezés, keressük meg
                        info = ydl.extract_info(f"ytsearch:{query}", download=False)
                        if not info or 'entries' not in info or not info['entries']:
                            return None
                        video = info['entries'][0]
                    
                    # Csak élő adásokat ellenőrizzük
                    if video.get('is_live', False):
                        return None  # Élő adások nem támogatottak
                    
                    # Ellenőrizzük, hogy a videó lejátszható-e
                    if not video.get('url') and not video.get('webpage_url'):
                        return None
                    
                    return {
                        'title': video.get('title', 'Ismeretlen cím'),
                        'duration': video.get('duration', 0),
                        'url': video.get('url') or video.get('webpage_url'),
                        'thumbnail': video.get('thumbnail'),
                        'webpage_url': video.get('webpage_url'),
                        'uploader': video.get('uploader', 'Ismeretlen feltöltő'),
                        'type': 'youtube'
                    }
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Ha DRM hiba, próbáljuk meg alternatív formátumokkal
                    if 'drm' in error_msg or 'protected' in error_msg:
                        try:
                            # Próbáljuk meg más formátumokkal
                            alt_opts = search_opts.copy()
                            alt_opts['format'] = 'bestaudio/best'
                            alt_opts['extractaudio'] = False  # Ne próbáljuk meg kivonni az audiót
                            
                            with yt_dlp.YoutubeDL(alt_opts) as ydl2:
                                if query.startswith(('http://', 'https://')):
                                    info = ydl2.extract_info(query, download=False)
                                    video = info
                                else:
                                    info = ydl2.extract_info(f"ytsearch:{query}", download=False)
                                    if not info or 'entries' not in info or not info['entries']:
                                        return None
                                    video = info['entries'][0]
                                
                                if video.get('is_live', False):
                                    return None
                                
                                if not video.get('url') and not video.get('webpage_url'):
                                    return None
                                
                                return {
                                    'title': video.get('title', 'Ismeretlen cím'),
                                    'duration': video.get('duration', 0),
                                    'url': video.get('url') or video.get('webpage_url'),
                                    'thumbnail': video.get('thumbnail'),
                                    'webpage_url': video.get('webpage_url'),
                                    'uploader': video.get('uploader', 'Ismeretlen feltöltő'),
                                    'type': 'youtube'
                                }
                        except:
                            pass  # Ha ez sem működik, akkor tényleg nem lejátszható
                    
                    print(f"Hiba a YouTube keresés során: {e}")
                    return None
                    
        except Exception as e:
            print(f"Hiba a YouTube keresés során: {e}")
            return None
    
    async def search_music(self, query: str) -> Optional[Dict]:
        """Univerzális zene keresés - Spotify és YouTube"""
        # Ha Spotify URL és nincs Spotify API, egyértelmű hibaüzenet
        if self.is_spotify_url(query) and not self.spotify:
            print("❌ Spotify URL érzékelve, de nincs Spotify API beállítva!")
            return None
        
        # Először próbáljuk meg a Spotify-t
        if self.spotify and (self.is_spotify_url(query) or 'spotify' in query.lower()):
            spotify_result = await self.search_spotify(query)
            if spotify_result:
                return spotify_result

        # Ha nem Spotify vagy nem találtunk semmit, próbáljuk meg a YouTube-ot
        youtube_result = await self.search_youtube(query)
        if youtube_result:
            return youtube_result

        # Ha Spotify eredményt találtunk, de YouTube-on nem, próbáljuk meg keresni az előadó + cím alapján
        if self.spotify and spotify_result:
            search_query = f"{spotify_result['artist']} {spotify_result['title']}"
            youtube_result = await self.search_youtube(search_query)
            if youtube_result:
                # Frissítjük a YouTube eredményt a Spotify információkkal
                youtube_result.update({
                    'spotify_info': spotify_result,
                    'type': 'spotify_youtube'
                })
                return youtube_result

        return None
    
    async def add_to_queue(self, interaction: discord.Interaction, query: str) -> bool:
        """Zene hozzáadása a várólistához"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Először csatlakozz egy hangcsatornához a `/music join` paranccsal!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        # Zene keresés
        await interaction.response.defer()
        
        music_info = await self.search_music(query)
        if not music_info:
            # Spotify specifikus hibaüzenet
            if self.is_spotify_url(query) and not self.spotify:
                embed = discord.Embed(
                    title="❌ Spotify Hiba!",
                    description=f"**Spotify link érzékelve, de nincs Spotify API beállítva!**\n\n"
                               f"🔗 **Link:** {query}\n\n"
                               "**🔧 Megoldás:**\n"
                               "• Állítsd be a Spotify API kulcsokat\n"
                               "• Indítsd újra a botot\n"
                               "• Vagy használj YouTube linket helyette\n\n"
                               "**📋 Spotify API kulcsok beszerzése:**\n"
                               "1. Menj a https://developer.spotify.com/dashboard/applications oldalra\n"
                               "2. Hozz létre egy új alkalmazást\n"
                               "3. Másold ki a Client ID és Client Secret kulcsokat\n"
                               "4. Indítsd újra a botot és add meg őket",
                    color=COLORS['ERROR']
                )
            else:
                embed = discord.Embed(
                    title="❌ Hiba!",
                    description=f"Nem találtam zenét a következő keresésre: **{query}**\n\n"
                               "**Lehetséges okok:**\n"
                               "• Élő adás (nem támogatott)\n"
                               "• A videó nem elérhető\n"
                               "• Érvénytelen URL vagy keresési kifejezés\n"
                               "• Spotify API nincs beállítva (Spotify linkek esetén)\n\n"
                               "**Próbáld meg:**\n"
                               "• Másik YouTube videót vagy Spotify linket\n"
                               "• Keresési kifejezést a videó neve alapján\n"
                               "• Bot újraindítása a Spotify API beállításához",
                    color=COLORS['ERROR']
                )
            await interaction.followup.send(embed=embed)
            return False
        
        # Ha playlist vagy album, minden számot hozzáadunk
        if music_info.get('type') in ['spotify_playlist', 'spotify_album'] and music_info.get('tracks'):
            tracks = music_info['tracks']
            added_count = 0
            
            for track in tracks:
                # Közvetlenül a Spotify track URL-t használjuk
                queue_item = {
                    'title': track['title'],
                    'duration': track.get('duration', 0),
                    'url': track['spotify_url'],  # Spotify URL közvetlenül
                    'thumbnail': track.get('thumbnail'),
                    'webpage_url': track['spotify_url'],
                    'uploader': track.get('artist', 'Ismeretlen előadó'),
                    'album': track.get('album'),
                    'type': 'spotify_track',  # Spotify track típus
                    'requester': interaction.user
                }
                
                self.queues[guild_id].append(queue_item)
                added_count += 1
            
            # Értesítés a playlist/album hozzáadásáról
            embed_color = COLORS['SPOTIFY']
            embed = discord.Embed(
                title="✅ Playlist/Album hozzáadva!",
                description=f"**{music_info['title']}** hozzáadva a várólistához!",
                color=embed_color
            )
            
            if music_info.get('thumbnail'):
                embed.set_thumbnail(url=music_info['thumbnail'])
            
            embed.add_field(
                name="📊 Hozzáadott számok",
                value=f"**{added_count}** szám a **{len(tracks)}**-ból",
                inline=True
            )
            
            embed.add_field(
                name="📋 Várólista",
                value=f"Pozíció: {len(self.queues[guild_id]) - added_count + 1} - {len(self.queues[guild_id])}",
                inline=True
            )
            
            embed.add_field(
                name="🎵 Kérte",
                value=interaction.user.mention,
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
            # Ha nincs zene lejátszásban, indítsuk el
            if not self.now_playing.get(guild_id):
                await self.play_next(interaction.guild)
            
            return True
        
        # Egyetlen zene hozzáadása
        queue_item = {
            'title': music_info['title'],
            'duration': music_info.get('duration', 0),
            'url': music_info.get('url') or music_info.get('spotify_url'),
            'thumbnail': music_info.get('thumbnail'),
            'webpage_url': music_info.get('webpage_url') or music_info.get('spotify_url'),
            'uploader': music_info.get('uploader') or music_info.get('artist', 'Ismeretlen előadó'),
            'album': music_info.get('album'),
            'type': music_info.get('type', 'unknown'),
            'requester': interaction.user
        }
        
        self.queues[guild_id].append(queue_item)
        
        # Embed szín beállítása a típus alapján
        embed_color = COLORS['SPOTIFY'] if 'spotify' in str(music_info.get('type', '')).lower() else COLORS['SUCCESS']
        
        embed = discord.Embed(
            title="✅ Zene hozzáadva!",
            description=f"**{music_info['title']}** hozzáadva a várólistához!",
            color=embed_color
        )
        
        if music_info.get('thumbnail'):
            embed.set_thumbnail(url=music_info['thumbnail'])
        
        # Előadó/Uploader információ
        if music_info.get('artist'):
            embed.add_field(
                name="👤 Előadó",
                value=music_info['artist'],
                inline=True
            )
        elif music_info.get('uploader'):
            embed.add_field(
                name="👤 Feltöltő",
                value=music_info['uploader'],
                inline=True
            )
        
        # Album információ (Spotify esetén)
        if music_info.get('album'):
            embed.add_field(
                name="💿 Album",
                value=music_info['album'],
                inline=True
            )
        
        # Hossz információ
        if music_info.get('duration'):
            duration = f"{music_info['duration']//60}:{music_info['duration']%60:02d}"
            embed.add_field(
                name="⏱️ Hossz",
                value=duration,
                inline=True
            )
        
        # Forrás típus
        source_type = "🎵 Spotify" if 'spotify' in str(music_info.get('type', '')).lower() else "📺 YouTube"
        embed.add_field(
            name="🔗 Forrás",
            value=source_type,
            inline=True
        )
        
        embed.add_field(
            name="📊 Várólista",
            value=f"Pozíció: {len(self.queues[guild_id])}",
            inline=True
        )
        
        # Kérte
        embed.add_field(
            name="🎵 Kérte",
            value=interaction.user.mention,
            inline=True
        )
        
        await interaction.followup.send(embed=embed)
        
        # Ha nincs zene lejátszásban, indítsuk el
        if not self.now_playing.get(guild_id):
            await self.play_next(interaction.guild)
        
        return True
    
    async def play_next(self, guild):
        """Következő zene lejátszása"""
        guild_id = guild.id
        
        if guild_id not in self.queues or not self.queues[guild_id]:
            self.now_playing[guild_id] = None
            return
        
        if guild_id not in self.voice_clients:
            return
        
        voice_client = self.voice_clients[guild_id]
        if not voice_client.is_connected():
            return
        
        try:
            # Következő zene a várólistából
            queue_item = self.queues[guild_id].popleft()
            self.now_playing[guild_id] = queue_item
            
            # FFmpeg ellenőrzés
            if not await self.check_ffmpeg():
                print("FFmpeg nincs telepítve!")
                return
            
            # Zene lejátszása
            try:
                # Ha Spotify URL, konvertáljuk YouTube-ra
                if queue_item.get('type') == 'spotify_track' and 'spotify.com' in str(queue_item.get('url', '')):
                    # Spotify track konvertálása YouTube-ra
                    search_query = f"{queue_item.get('uploader', '')} {queue_item.get('title', '')}"
                    youtube_result = await self.search_youtube(search_query)
                    
                    if youtube_result:
                        # YouTube URL használata a lejátszáshoz
                        play_url = youtube_result.get('url')
                        print(f"Spotify track konvertálva YouTube-ra: {search_query}")
                    else:
                        # Ha nem találjuk meg YouTube-on, próbáljuk meg a Spotify URL-t
                        play_url = queue_item.get('url')
                        print(f"Spotify track nem található YouTube-on, Spotify URL használata")
                else:
                    # Normál URL (YouTube vagy más)
                    play_url = queue_item.get('url')
                
                source = discord.FFmpegPCMAudio(
                    play_url,
                    **self.ffmpeg_options
                )
                
                # Hangerej beállítása
                source = discord.PCMVolumeTransformer(source)
                source.volume = 0.5
                
                voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(guild)))
                
                # Értesítés a lejátszásról
                embed = discord.Embed(
                    title="🎵 Most játszik",
                    description=f"**{queue_item['title']}**",
                    color=COLORS['SPOTIFY'] if 'spotify' in str(queue_item.get('type', '')).lower() else COLORS['SUCCESS']
                )
                
                if queue_item['thumbnail']:
                    embed.set_thumbnail(url=queue_item['thumbnail'])
                
                # Előadó/Uploader információ
                if queue_item.get('artist'):
                    embed.add_field(
                        name="👤 Előadó",
                        value=queue_item['artist'],
                        inline=True
                    )
                elif queue_item.get('uploader'):
                    embed.add_field(
                        name="👤 Feltöltő",
                        value=queue_item['uploader'],
                        inline=True
                    )
                
                # Album információ (Spotify esetén)
                if queue_item.get('album'):
                    embed.add_field(
                        name="💿 Album",
                        value=queue_item['album'],
                        inline=True
                    )
                
                # Hossz információ
                if queue_item.get('duration'):
                    duration = f"{queue_item['duration']//60}:{queue_item['duration']%60:02d}"
                    embed.add_field(
                        name="⏱️ Hossz",
                        value=duration,
                        inline=True
                    )
                
                embed.add_field(
                    name="👤 Kérte",
                    value=queue_item['requester'].mention,
                    inline=True
                )
                
                # Forrás típus
                source_type = "🎵 Spotify" if 'spotify' in str(queue_item.get('type', '')).lower() else "📺 YouTube"
                embed.add_field(
                    name="🔗 Forrás",
                    value=source_type,
                    inline=True
                )
                
                # Várólista hossz
                remaining = len(self.queues[guild_id])
                if remaining > 0:
                    embed.add_field(
                        name="📋 Várólista",
                        value=f"Még {remaining} szám vár",
                        inline=True
                    )
                
                # Csatorna keresése az értesítéshez
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        try:
                            await channel.send(embed=embed)
                            break
                        except:
                            continue
                
            except Exception as e:
                print(f"Hiba a következő szám lejátszása során: {e}")
                
                # Részletes hibaüzenet
                error_embed = discord.Embed(
                    title="❌ Hiba a lejátszás során!",
                    description=f"**{queue_item['title']}** nem játszható le!\n\n"
                               f"**Hiba:** {str(e)}\n\n"
                               "**Próbáljuk meg a következő számot...**",
                    color=0xff0000
                )
                
                # Csatorna keresése a hibaüzenethez
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        try:
                            await channel.send(embed=error_embed)
                            break
                        except:
                            continue
                
                # Próbáljuk meg a következő számot
                await self.play_next(guild)
                
        except Exception as e:
            print(f"Hiba a play_next során: {e}")
            self.now_playing[guild_id] = None
    
    async def skip(self, interaction: discord.Interaction) -> bool:
        """Következő szám"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(
                title="⏭️ Kihagyva!",
                description="A jelenlegi szám kihagyva!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Jelenleg nincs zene lejátszásban!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    async def pause(self, interaction: discord.Interaction) -> bool:
        """Szüneteltetés"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(
                title="⏸️ Szüneteltetve!",
                description="A zene szüneteltetve!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Jelenleg nincs zene lejátszásban!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    async def resume(self, interaction: discord.Interaction) -> bool:
        """Folytatás"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(
                title="▶️ Folytatva!",
                description="A zene folytatódik!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="A zene nincs szüneteltetve!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    async def stop(self, interaction: discord.Interaction) -> bool:
        """Leállítás"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
            self.queues[guild_id].clear()
            self.now_playing[guild_id] = None
            
            embed = discord.Embed(
                title="⏹️ Leállítva!",
                description="A zene leállítva és a várólista törölve!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Jelenleg nincs zene lejátszásban!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    async def set_volume(self, interaction: discord.Interaction, volume: int) -> bool:
        """Hangerej beállítása"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        if not 0 <= volume <= 100:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="A hangerej 0-100 között kell lennie!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.source and hasattr(voice_client.source, 'volume'):
            voice_client.source.volume = volume / 100.0
            
            embed = discord.Embed(
                title="🔊 Hangerej!",
                description=f"A hangerej beállítva: **{volume}%**",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            return True
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem sikerült beállítani a hangerejt!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
    
    async def show_queue(self, interaction: discord.Interaction) -> bool:
        """Várólista megjelenítése"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.queues:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        queue = self.queues[guild_id]
        now_playing = self.now_playing.get(guild_id)
        
        embed = discord.Embed(
            title="📋 Várólista",
            color=0x0099ff
        )
        
        if now_playing:
            # Forrás típus meghatározása
            source_type = "🎵 Spotify" if 'spotify' in str(now_playing.get('type', '')).lower() else "📺 YouTube"
            
            now_playing_text = f"**{now_playing['title']}**\n{source_type}"
            
            # Spotify link hozzáadása (ha van)
            if now_playing.get('spotify_url'):
                now_playing_text += f"\n[🎵 Spotify Link]({now_playing['spotify_url']})"
            
            embed.add_field(
                name="🎵 Most játszik",
                value=now_playing_text,
                inline=False
            )
        
        if queue:
            queue_text = ""
            for i, item in enumerate(queue[:10], 1):  # Csak az első 10 elem
                duration = f" ({item['duration']//60}:{item['duration']%60:02d})" if item.get('duration') else ""
                source_type = "🎵" if 'spotify' in str(item.get('type', '')).lower() else "📺"
                
                item_text = f"{i}. {source_type} **{item['title']}**{duration}"
                
                # Spotify link hozzáadása (ha van)
                if item.get('spotify_url'):
                    item_text += f" - [🎵 Spotify]({item['spotify_url']})"
                
                queue_text += item_text + "\n"
            
            if len(queue) > 10:
                queue_text += f"\n... és még {len(queue) - 10} szám"
            
            embed.add_field(
                name=f"⏭️ Következő ({len(queue)} szám)",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="⏭️ Következő",
                value="A várólista üres!",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        return True
    
    async def show_now_playing(self, interaction: discord.Interaction) -> bool:
        """Aktuális szám megjelenítése"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.now_playing or not self.now_playing[guild_id]:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Jelenleg nincs zene lejátszásban!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        now_playing = self.now_playing[guild_id]
        
        # Forrás típus meghatározása
        source_type = "🎵 Spotify" if 'spotify' in str(now_playing.get('type', '')).lower() else "📺 YouTube"
        embed_color = COLORS['SPOTIFY'] if 'spotify' in str(now_playing.get('type', '')).lower() else COLORS['SUCCESS']
        
        embed = discord.Embed(
            title="🎵 Most játszik",
            description=f"**{now_playing['title']}**",
            color=embed_color
        )
        
        if now_playing['thumbnail']:
            embed.set_thumbnail(url=now_playing['thumbnail'])
        
        # Előadó/Uploader információ
        if now_playing.get('artist'):
            embed.add_field(
                name="👤 Előadó",
                value=now_playing['artist'],
                inline=True
            )
        elif now_playing.get('uploader'):
            embed.add_field(
                name="👤 Feltöltő",
                value=now_playing['uploader'],
                inline=True
            )
        
        # Album információ (Spotify esetén)
        if now_playing.get('album'):
            embed.add_field(
                name="💿 Album",
                value=now_playing['album'],
                inline=True
            )
        
        if now_playing.get('duration'):
            duration = f"{now_playing['duration']//60}:{now_playing['duration']%60:02d}"
            embed.add_field(
                name="⏱️ Hossz",
                value=duration,
                inline=True
            )
        
        embed.add_field(
            name="👤 Kérte",
            value=now_playing['requester'].mention,
            inline=True
        )
        
        # Forrás típus
        embed.add_field(
            name="🔗 Forrás",
            value=source_type,
            inline=True
        )
        
        # Spotify link megjelenítése (ha van)
        if now_playing.get('spotify_url'):
            embed.add_field(
                name="🎵 Spotify Link",
                value=f"[Nyisd meg Spotify-on]({now_playing['spotify_url']})",
                inline=False
            )
        
        # Az üzenetet a parancs küldi el, nem itt
        return True
    
    async def clear_queue(self, interaction: discord.Interaction) -> bool:
        """Várólista törlése"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.queues:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagyok hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return False
        
        queue_length = len(self.queues[guild_id])
        self.queues[guild_id].clear()
        
        embed = discord.Embed(
            title="🗑️ Várólista törölve!",
            description=f"**{queue_length}** szám eltávolítva a várólistából!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
        return True
