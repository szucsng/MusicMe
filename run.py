#!/usr/bin/env python3
"""
🎵 Discord Zene Bot - Intelligens indítási fájl
"""

import os
import sys
import asyncio

def check_python_version():
    """Ellenőrzi a Python verziót és visszaadja a megfelelő bot típust"""
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13+ észlelve - voice funkciók nem működnek")
        print("   A minimális bot verziót fogom használni")
        return "minimal"
    elif version.major == 3 and version.minor >= 7:
        print("✅ Python verzió kompatibilis a teljes zene bot funkciókkal")
        return "full"
    else:
        print("❌ Python 3.7+ szükséges!")
        return None

def setup_token():
    """Bot token beállítása"""
    token = input("🎵 Kérlek add meg a Discord bot token-t: ").strip()
    if not token:
        print("❌ Hiba: Token megadása kötelező!")
        sys.exit(1)
    
    # Token beállítása környezeti változóként
    os.environ['BOT_TOKEN'] = token
    print("✅ Bot token beállítva!")
    return token

async def run_minimal_bot(token):
    """Minimális bot futtatása (Python 3.13+ kompatibilis)"""
    try:
        from minimal_bot import MinimalDiscordBot
        print("🚀 Minimális bot indítása...")
        bot = MinimalDiscordBot(token)
        await bot.start()
    except ImportError as e:
        print(f"❌ Import hiba: {e}")
        print("A minimal_bot.py fájl nem található!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Minimális bot hiba: {e}")
        sys.exit(1)

async def run_full_bot(token):
    """Teljes zene bot futtatása (Python 3.12 vagy korábbi)"""
    try:
        from bot import MusicBot
        print("🚀 Teljes zene bot indítása...")
        bot = MusicBot()
        await bot.start(token)
    except ImportError as e:
        print(f"❌ Import hiba: {e}")
        print("Kérlek telepítsd a szükséges csomagokat: py -3.12 -m pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Teljes bot hiba: {e}")
        sys.exit(1)

async def main():
    """Fő függvény"""
    print("🎵 Discord Zene Bot - Intelligens indítási rendszer")
    print("=" * 50)
    
    # Python verzió ellenőrzése
    bot_type = check_python_version()
    if not bot_type:
        sys.exit(1)
    
    print()
    
    # Token beállítása
    token = setup_token()
    
    # Megfelelő bot indítása
    if bot_type == "minimal":
        await run_minimal_bot(token)
    else:
        await run_full_bot(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot leállítva!")
    except Exception as e:
        print(f"❌ Váratlan hiba: {e}")
        print("\n🔧 Hibaelhárítás:")
        print("1. Ellenőrizd a Python verziót: py -3.12 --version")
        print("2. Telepítsd a függőségeket: py -3.12 -m pip install -r requirements.txt")
        print("3. Python 3.13+ esetén használd: python minimal_bot.py")
