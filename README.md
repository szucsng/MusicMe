# 🎵 Discord Zene Bot

Egy teljes funkcionalitású Discord zene bot, amely YouTube-ról tud zenét lejátszani. Magyar nyelvű felülettel és intuitív parancsokkal rendelkezik.

## ✨ Funkciók

- 🎵 YouTube zene lejátszás
- 📋 Várólista kezelés
- 🔊 Hangerej szabályozás
- ⏯️ Lejátszás vezérlése (play, pause, resume, skip, stop)
- 🌐 Támogatja a YouTube URL-eket és kereséseket
- 🎨 Szép Discord embed üzenetek
- 🇭🇺 Magyar nyelvű parancsok és alias-ok

## 🚀 Telepítés

### 1. Python 3.12 telepítése

**Fontos:** A teljes zene bot funkciókhoz Python 3.12 vagy korábbi verzió szükséges!

**Windows:**
- Töltsd le a Python 3.12-t innen: https://www.python.org/downloads/release/python-3120/
- Válaszd ki a "Windows installer (64-bit)" opciót
- Telepítés közben kapcsold be a "Add Python to PATH" opciót

**macOS:**
```bash
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-pip
```

### 2. Függőségek telepítése

```bash
# Windows
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pip install PyNaCl

# Linux/macOS
python3.12 -m pip install -r requirements.txt
python3.12 -m pip install PyNaCl
```

### 3. FFmpeg telepítése

A bot működéséhez szükséges az FFmpeg:

**Windows:**
- Töltsd le az FFmpeg-et innen: https://ffmpeg.org/download.html
- Add hozzá a PATH-hoz
- winget install Gyan.FFmpeg parancs powershellben

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Discord Bot létrehozása

1. Menj a [Discord Developer Portal](https://discord.com/developers/applications)-ra
2. Kattints az "New Application" gombra
3. Add meg a bot nevét
4. Menj a "Bot" szekcióba
5. Kattints az "Add Bot" gombra
6. Másold ki a bot token-t
7. Kapcsold be a "Message Content Intent" opciót

### 5. Bot token beállítása

A bot automatikusan bekéri a token-t indításkor, de ha szeretnéd manuálisan beállítani:

1. Nevezd át az `env_example.txt` fájlt `.env`-re
2. Cseréld ki a `your_bot_token_here` részt a saját bot token-eddel

```env
BOT_TOKEN=your_actual_bot_token_here
BOT_PREFIX=!
```

**Megjegyzés:** A `run.py` fájl használatakor a bot automatikusan bekéri a token-t!

### 6. Bot meghívása a szerveredre

1. Menj a "OAuth2" > "URL Generator" szekcióba
2. Válaszd ki a "bot" scope-ot
3. Válaszd ki a szükséges jogosultságokat:
   - **Send Messages** - Üzenetek küldése
   - **Use Slash Commands** - Slash parancsok használata (kötelező!)
   - **Connect** - Hangcsatornához csatlakozás
   - **Speak** - Hangcsatornában beszéd
   - **Use Voice Activity** - Voice aktivitás használata
   - **Embed Links** - Linkek beágyazása
4. Használd a generált URL-t a bot meghívásához

**Fontos:** A "Use Slash Commands" jogosultság kötelező a slash parancsok működéséhez!

## 🎮 Parancsok

**Fontos:** A bot most slash parancsokat használ! Írd be a `/` jelet, és a Discord automatikusan megjeleníti az elérhető parancsokat, mint a képen látható.

### Hangcsatorna parancsok
- `/music join` - Csatlakozás a hangcsatornához
- `/music leave` - Kilépés a hangcsatornából

### Zene lejátszás
- `/music play <query>` - YouTube zene lejátszása (URL vagy keresési kifejezés)
- `/music skip` - Következő szám
- `/music pause` - Szüneteltetés
- `/music resume` - Folytatás
- `/music stop` - Leállítás

### Várólista kezelés
- `/music queue` - Várólista megjelenítése
- `/music nowplaying` - Aktuális szám
- `/music clear` - Várólista törlése

### Beállítások
- `/music volume <0-100>` - Hangerej beállítása

### Segítség
- `/help help` - Segítség megjelenítése

**Megjegyzés:** A Discord automatikusan kezeli a slash parancsokat! Amikor beírod a `/` jelet, a bot automatikusan megjeleníti az elérhető parancsokat és a paramétereket, ahogy a képen látható.

## 🧪 Tesztelés

Mielőtt elindítanád a botot, teszteld, hogy minden megfelelően működik:

```bash
# Windows
py -3.12 test_bot.py

# Linux/macOS
python3.12 test_bot.py
```

## ⚠️ Python Verzió Kompatibilitás

**Fontos:** A voice funkciók csak Python 3.12 vagy korábbi verziókban működnek!

### Python verziók:
- ✅ **Python 3.7 - 3.12**: Teljes zene bot funkciók
- ❌ **Python 3.13+**: Voice funkciók nem működnek (audioop modul hiánya)

### Megoldások Python 3.13+ esetén:
1. **Python 3.12 telepítése** (ajánlott)
2. **Minimális bot használata** (`minimal_bot.py`) - alapvető Discord funkciók, voice nélkül

## 🏃‍♂️ Indítás

### Automatikus indítás (ajánlott)
- **Windows:** `start.bat` (Python 3.12-t használ)
- **Linux/macOS:** `./start.sh` (Python 3.12-t használ)

### Manuális indítás
```bash
# Windows
py -3.12 run.py

# Linux/macOS
python3.12 run.py
```

### Minimális bot (Python 3.13+ esetén)
```bash
# Függőségek telepítése
pip install aiohttp

# Minimális bot indítása
python minimal_bot.py
```

## 📁 Fájl struktúra

```
music/
├── bot.py              # Fő bot fájl (teljes zene bot)
├── music_player.py     # Zene lejátszó logika
├── music_commands.py   # Bot parancsok
├── config.py           # Konfiguráció
├── run.py              # Intelligens indítási fájl
├── simple_bot.py       # Egyszerű bot (voice nélkül)
├── minimal_bot.py      # Minimális bot (Python 3.13 kompatibilis)
├── test_bot.py         # Tesztelési fájl
├── requirements.txt    # Python függőségek
├── start.bat           # Windows indítási fájl (Python 3.12)
├── start.sh            # Linux/macOS indítási fájl (Python 3.12)
├── env_example.txt     # Környezeti változók példa
└── README.md           # Ez a fájl
```

## 🔧 Hibaelhárítás

### "FFmpeg not found" hiba
- Győződj meg róla, hogy az FFmpeg telepítve van és a PATH-ban van

### "Invalid token" hiba
- Ellenőrizd, hogy a `.env` fájlban helyesen van-e beállítva a bot token
- Vagy használd a `run.py` fájlt, amely bekéri a token-t

### Bot nem csatlakozik a hangcsatornához
- Ellenőrizd, hogy a bot rendelkezik-e a szükséges jogosultságokkal
- Győződj meg róla, hogy a "Connect" és "Speak" jogosultságok be vannak kapcsolva

### Slash parancsok nem jelennek meg
- **Ellenőrizd a "Use Slash Commands" jogosultságot** - ez kötelező!
- Várj 1-2 percet a parancsok szinkronizálásához
- Indítsd újra a botot
- Ellenőrizd, hogy a bot rendelkezik-e a megfelelő jogosultságokkal

### Python verzió problémák
- **"No module named 'audioop'" hiba:** Használj Python 3.12-t
- **Voice funkciók nem működnek:** Ellenőrizd a Python verziót
- **Import hibák:** Telepítsd újra a függőségeket a megfelelő Python verzióval

## 🤝 Közreműködés

Ha szeretnél hozzájárulni a projekthez, kérlek:

1. Fork-old a projektet
2. Hozz létre egy feature branch-et
3. Commit-old a változtatásaidat
4. Push-old a branch-et
5. Nyiss egy Pull Request-et

## 📄 Licenc

Ez a projekt MIT licenc alatt áll.

## 🆘 Támogatás

Ha problémába ütközöl, kérlek:

1. **Ellenőrizd a README-t** - különös tekintettel a Python verzió kompatibilitásra
2. **Nézd meg a konzol üzeneteket** - a hibaüzenetek segítenek a probléma azonosításában
3. **Győződj meg róla, hogy Python 3.12-t használsz** a teljes zene bot funkciókhoz
4. **Telepítsd a függőségeket a megfelelő Python verzióval** - `py -3.12 -m pip install -r requirements.txt`
5. **Ha továbbra is problémába ütközöl**, nyiss egy Issue-t

### Gyakori problémák és megoldások:

- **"No module named 'audioop'"** → Használj Python 3.12-t
- **Voice funkciók nem működnek** → Ellenőrizd a Python verziót
- **Import hibák** → Telepítsd újra a függőségeket Python 3.12-vel
- **Python 3.13+ problémák** → Telepítsd a Python 3.12-t

---

**Jó szórakozást a zenéléssel! 🎵**
