import discord
from discord.ext import commands
import asyncio
import os
from config import BOT_PREFIX
from music_commands import setup as setup_music

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=intents,
            help_command=None,
            description="🎵 Discord Zene Bot - Magyar nyelvű zene lejátszó bot"
        )
        
        self.initial_extensions = []
    
    async def setup_hook(self):
        """Bot indításakor fut le"""
        print("🎵 Discord Zene Bot indítása...")
        
        # Zene parancsok betöltése
        try:
            setup_music(self)
            print("✅ Zene parancsok betöltve!")
        except Exception as e:
            print(f"❌ Hiba a zene parancsok betöltése során: {e}")
        
        # Slash parancsok regisztrálása és szinkronizálása
        try:
            await self.tree.sync()
            print("✅ Slash parancsok szinkronizálva!")
        except Exception as e:
            print(f"❌ Hiba a slash parancsok szinkronizálása során: {e}")
        
        print("✅ Bot beállítások kész!")
    
    async def on_ready(self):
        """Bot sikeresen elindult"""
        print(f"🎵 {self.user} sikeresen elindult!")
        print(f"📊 {len(self.guilds)} szerveren vagyok jelen")
        print(f"👥 {len(self.users)} felhasználóval kapcsolódok")
        
        # Slash parancsok újra szinkronizálása minden szerveren
        try:
            await self.tree.sync()
            print("✅ Slash parancsok minden szerveren szinkronizálva!")
        except Exception as e:
            print(f"❌ Hiba a slash parancsok szinkronizálása során: {e}")
        
        # Bot státusz beállítása
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/music play | Zene lejátszás"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Parancs hibák kezelése"""
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="❌ Ismeretlen parancs!",
                description=f"A `{ctx.message.content}` parancs nem létezik!\n"
                           f"Használd a `/help help` parancsot a segítségért!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Hiányzó argumentum!",
                description=f"A `{ctx.command.name}` parancshoz szükséges argumentum hiányzik!\n"
                           f"Használat: `/{ctx.command.name} {ctx.command.signature}`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        else:
            embed = discord.Embed(
                title="❌ Hiba történt!",
                description=f"Váratlan hiba: {str(error)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            print(f"Hiba a {ctx.command.name} parancsnál: {error}")

def setup_environment():
    """Környezeti változók beállítása"""
    # .env fájl létrehozása ha nem létezik
    env_file = '.env'
    if not os.path.exists(env_file):
        print("📁 .env fájl létrehozása...")
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# Discord Bot Token\n")
                f.write("BOT_TOKEN=your_bot_token_here\n\n")
                f.write("# Spotify API kulcsok - KÖTELEZŐ a Spotify támogatáshoz!\n")
                f.write("# Szerezd be innen: https://developer.spotify.com/dashboard/applications\n")
                f.write("SPOTIFY_CLIENT_ID=your_spotify_client_id_here\n")
                f.write("SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here\n\n")
                f.write("# Bot prefix\n")
                f.write("BOT_PREFIX=!\n")
            print("✅ .env fájl létrehozva!")
        except Exception as e:
            print(f"⚠️ Nem sikerült létrehozni a .env fájlt: {e}")

def get_bot_token():
    """Bot token beállítása"""
    # Először próbáljuk a környezeti változóból
    token = os.getenv('BOT_TOKEN')

    if not token or token == 'your_bot_token_here':
        # Ha nincs, bekérjük a felhasználótól
        print("🎵 Discord Zene Bot - Slash parancsokkal")
        print("=" * 50)
        print("📋 Kérlek állítsd be a következőket:")
        print()
        
        # Bot token bekérése
        token = input("🎵 Discord bot token: ").strip()
        if not token:
            print("❌ Hiba: Token megadása kötelező!")
            return None

        # Spotify API kulcsok bekérése
        print("\n🎵 Spotify API beállítása (opcionális, de ajánlott):")
        print("   Szerezd be innen: https://developer.spotify.com/dashboard/applications")
        spotify_id = input("🎵 Spotify Client ID (vagy Enter a kihagyáshoz): ").strip()
        spotify_secret = input("🎵 Spotify Client Secret (vagy Enter a kihagyáshoz): ").strip()

        # Környezeti változók beállítása
        os.environ['BOT_TOKEN'] = token
        if spotify_id:
            os.environ['SPOTIFY_CLIENT_ID'] = spotify_id
        if spotify_secret:
            os.environ['SPOTIFY_CLIENT_SECRET'] = spotify_secret

        # .env fájl frissítése
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(f"# Discord Bot Token\n")
                f.write(f"BOT_TOKEN={token}\n\n")
                f.write(f"# Spotify API kulcsok\n")
                f.write(f"SPOTIFY_CLIENT_ID={spotify_id if spotify_id else 'your_spotify_client_id_here'}\n")
                f.write(f"SPOTIFY_CLIENT_SECRET={spotify_secret if spotify_secret else 'your_spotify_client_secret_here'}\n\n")
                f.write(f"# Bot prefix\n")
                f.write(f"BOT_PREFIX=!\n")
            print("✅ Beállítások mentve a .env fájlba!")
        except Exception as e:
            print(f"⚠️ Nem sikerült menteni a .env fájlt: {e}")

    return token

async def main():
    """Fő függvény"""
    # Környezet beállítása
    setup_environment()
    
    # Bot token beállítása
    token = get_bot_token()
    if not token:
        return
    
    print("✅ Bot token beállítva!")
    
    bot = MusicBot()
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Hiba: Érvénytelen bot token!")
    except Exception as e:
        print(f"❌ Váratlan hiba: {e}")

if __name__ == "__main__":
    asyncio.run(main())
