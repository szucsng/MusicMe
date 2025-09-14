#!/usr/bin/env python3
"""
🧪 Discord Zene Bot - Tesztelési fájl
"""

import sys

def check_python_version():
    """Ellenőrzi a Python verziót"""
    version = sys.version_info
    print(f"🐍 Python verzió: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13+ észlelve - voice funkciók kompatibilitási problémákkal rendelkezhetnek")
        return False
    elif version.major == 3 and version.minor >= 7:
        print("✅ Python verzió kompatibilis")
        return True
    else:
        print("❌ Python 3.7+ szükséges!")
        return False

def test_basic_imports():
    """Teszteli az alapvető importokat (discord nélkül)"""
    try:
        import yt_dlp
        print("✅ yt-dlp importálva")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv importálva")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import hiba: {e}")
        return False

def test_config():
    """Teszteli a konfigurációs fájlt"""
    try:
        from config import COLORS, BOT_PREFIX
        print("✅ Konfiguráció betöltve")
        print(f"   Bot prefix: {BOT_PREFIX}")
        print(f"   Színek: {len(COLORS)} db")
        return True
        
    except Exception as e:
        print(f"❌ Konfigurációs hiba: {e}")
        return False

def test_file_structure():
    """Teszteli a fájl struktúrát"""
    import os
    
    required_files = [
        'bot.py',
        'music_player.py', 
        'music_commands.py',
        'config.py',
        'run.py',
        'requirements.txt',
        'start.bat',
        'start.sh',
        'env_example.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Hiányzó fájlok: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Minden szükséges fájl megtalálható")
        return True

def test_discord_compatibility():
    """Teszteli a Discord kompatibilitást"""
    try:
        import discord
        print("✅ discord.py importálva")
        
        # Próbáljuk importálni a voice funkciókat
        try:
            from discord import FFmpegPCMAudio
            print("✅ Voice funkciók kompatibilisek")
            return True
        except ImportError as e:
            print(f"⚠️  Voice funkciók nem kompatibilisek: {e}")
            print("   Ez normális Python 3.13+ esetén")
            return False
            
    except ImportError as e:
        print(f"❌ Discord import hiba: {e}")
        return False
    except Exception as e:
        print(f"❌ Discord tesztelési hiba: {e}")
        return False

def main():
    """Fő tesztelési függvény"""
    print("🧪 Discord Zene Bot tesztelése...")
    print("=" * 50)
    
    # Python verzió ellenőrzése
    python_ok = check_python_version()
    print()
    
    tests = [
        ("Fájl struktúra tesztelése", test_file_structure),
        ("Alapvető importok tesztelése", test_basic_imports),
        ("Konfiguráció tesztelése", test_config),
        ("Discord kompatibilitás tesztelése", test_discord_compatibility),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} sikeres!")
        else:
            print(f"❌ {test_name} sikertelen!")
    
    print("\n" + "=" * 50)
    print(f"📊 Eredmény: {passed}/{total} teszt sikeres")
    
    if passed >= 3:  # Legalább 3 tesztnek sikeresnek kell lennie
        print("🎉 A bot alapvetően működőképes!")
        print("\n🚀 Indítás:")
        print("   Windows: start.bat")
        print("   Linux/macOS: ./start.sh")
        print("   Manuális: python run.py")
        
        if not python_ok:
            print("\n⚠️  Figyelem: Python 3.13+ kompatibilitási problémák miatt")
            print("   használd a run.py fájlt a bot indításához!")
            
    else:
        print("⚠️  Túl sok teszt sikertelen. Kérlek ellenőrizd a hibákat!")
        print("\n🔧 Hibaelhárítás:")
        print("   1. Telepítsd a függőségeket: pip install -r requirements.txt")
        print("   2. Ellenőrizd, hogy Python 3.7+ van-e telepítve")
        print("   3. Ellenőrizd a fájl jogosultságokat")
        print("   4. Python 3.13 voice kompatibilitási problémák esetén használd a run.py fájlt")

if __name__ == "__main__":
    main()
