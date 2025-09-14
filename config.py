import os
from dotenv import load_dotenv

load_dotenv()

# Bot konfiguráció
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_PREFIX = '/'

# Spotify API kulcsok
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Zene bot beállítások
MAX_QUEUE_SIZE = 100
DEFAULT_VOLUME = 0.5
MAX_PLAYLIST_SIZE = 50

# Színkódok a Discord üzenetekhez
COLORS = {
    'SUCCESS': 0x00ff00,  # Zöld
    'ERROR': 0xff0000,    # Piros
    'INFO': 0x0099ff,     # Kék
    'WARNING': 0xffff00,  # Sárga
    'SPOTIFY': 0x1DB954   # Spotify zöld
}
