#!/usr/bin/env python3
"""
🎵 Discord Zene Bot - Egyszerű verzió Python 3.13 kompatibilitással
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands

# Bot konfiguráció
BOT_PREFIX = '!'
COLORS = {
    'SUCCESS': 0x00ff00,  # Zöld
    'ERROR': 0xff0000,    # Piros
    'INFO': 0x0099ff,     # Kék
    'WARNING': 0xffff00   # Sárga
}

class SimpleMusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=intents,
            help_command=None,
            description="🎵 Discord Zene Bot - Egyszerű verzió"
        )
    
    async def setup_hook(self):
        """Bot indításakor fut le"""
        print("🎵 Egyszerű Discord Zene Bot indítása...")
        
        # Egyszerű parancsok
        @self.command(name='ping', aliases=['ping'])
        async def ping_command(ctx):
            """Ping parancs"""
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Bot késleltetés: **{round(self.latency * 1000)}ms**",
                color=COLORS['SUCCESS']
            )
            await ctx.send(embed=embed)
        
        @self.command(name='info', aliases=['információ'])
        async def info_command(ctx):
            """Bot információk"""
            embed = discord.Embed(
                title="ℹ️ Bot Információk",
                description="Egyszerű Discord Zene Bot",
                color=COLORS['INFO']
            )
            embed.add_field(name="Bot prefix", value=BOT_PREFIX, inline=True)
            embed.add_field(name="Szerverek", value=len(self.guilds), inline=True)
            embed.add_field(name="Felhasználók", value=len(self.users), inline=True)
            embed.add_field(name="Python verzió", value=sys.version.split()[0], inline=True)
            embed.add_field(name="Discord.py verzió", value=discord.__version__, inline=True)
            embed.set_footer(text="Egyszerű verzió - Voice funkciók nélkül")
            await ctx.send(embed=embed)
        
        @self.command(name='help', aliases=['segítség', 'h'])
        async def help_command(ctx):
            """Segítség"""
            embed = discord.Embed(
                title="🎵 Egyszerű Discord Zene Bot - Segítség",
                description="Ez egy egyszerű verzió, voice funkciók nélkül.",
                color=COLORS['INFO']
            )
            
            embed.add_field(
                name="🔧 Alapvető parancsok:",
                value="`!ping` - Bot késleltetés\n"
                      "`!info` - Bot információk\n"
                      "`!help` - Ez a segítség",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Fontos:",
                value="Ez egy egyszerű verzió, amely nem támogatja a voice funkciókat.\n"
                      "A teljes zene bot használatához Python 3.12 vagy korábbi verzió szükséges.",
                inline=False
            )
            
            embed.set_footer(text="Bot prefix: ! | Egyszerű verzió")
            await ctx.send(embed=embed)
        
        print("✅ Alapvető parancsok beállítva!")
    
    async def on_ready(self):
        """Bot sikeresen elindult"""
        print(f"🎵 {self.user} sikeresen elindult!")
        print(f"📊 {len(self.guilds)} szerveren vagyok jelen")
        print(f"👥 {len(self.users)} felhasználóval kapcsolódok")
        
        # Bot státusz beállítása
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="!help | Egyszerű verzió"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Parancs hibák kezelése"""
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="❌ Ismeretlen parancs!",
                description=f"A `{ctx.message.content}` parancs nem létezik!\n"
                           f"Használd a `{BOT_PREFIX}help` parancsot a segítségért!",
                color=COLORS['ERROR']
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Hiba történt!",
                description=f"Váratlan hiba: {str(error)}",
                color=COLORS['ERROR']
            )
            await ctx.send(embed=embed)
            print(f"Hiba a {ctx.command.name if ctx.command else 'unknown'} parancsnál: {error}")

async def main():
    """Fő függvény"""
    print("🎵 Egyszerű Discord Zene Bot indítása...")
    print("⚠️  Ez egy egyszerű verzió, voice funkciók nélkül!")
    print("    A teljes zene bot használatához Python 3.12 vagy korábbi verzió szükséges.")
    print()
    
    # Bot token beállítása
    token = os.getenv('BOT_TOKEN')
    if not token:
        token = input("🎵 Kérlek add meg a Discord bot token-t: ").strip()
        if not token:
            print("❌ Hiba: Token megadása kötelező!")
            return
    
    # Bot indítása
    bot = SimpleMusicBot()
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Hiba: Érvénytelen bot token!")
    except Exception as e:
        print(f"❌ Váratlan hiba: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot leállítva!")
    except Exception as e:
        print(f"❌ Hiba: {e}")
