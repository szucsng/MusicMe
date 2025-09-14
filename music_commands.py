import discord
from discord import app_commands
from discord.ui import View, Button
from music_player import MusicPlayer

class MusicControlView(View):
    def __init__(self, music_player: MusicPlayer):
        super().__init__(timeout=None)  # A gombok soha nem járnak le
        self.music_player = music_player
        
        # Play/Pause gomb
        self.play_pause_button = Button(
            style=discord.ButtonStyle.primary,
            label="▶️ Lejátszás",
            custom_id="play_pause",
            emoji="▶️"
        )
        self.play_pause_button.callback = self.play_pause_callback
        self.add_item(self.play_pause_button)
        
        # Stop gomb
        self.stop_button = Button(
            style=discord.ButtonStyle.danger,
            label="⏹️ Leállítás",
            custom_id="stop",
            emoji="⏹️"
        )
        self.stop_button.callback = self.stop_callback
        self.add_item(self.stop_button)
        
        # Skip gomb
        self.skip_button = Button(
            style=discord.ButtonStyle.secondary,
            label="⏭️ Következő",
            custom_id="skip",
            emoji="⏭️"
        )
        self.skip_button.callback = self.skip_callback
        self.add_item(self.skip_button)
        
        # Volume gombok
        self.volume_down_button = Button(
            style=discord.ButtonStyle.secondary,
            label="🔉",
            custom_id="volume_down",
            emoji="🔉"
        )
        self.volume_down_button.callback = self.volume_down_callback
        self.add_item(self.volume_down_button)
        
        self.volume_up_button = Button(
            style=discord.ButtonStyle.secondary,
            label="🔊",
            custom_id="volume_up",
            emoji="🔊"
        )
        self.volume_up_button.callback = self.volume_up_callback
        self.add_item(self.volume_up_button)
    
    async def play_pause_callback(self, interaction: discord.Interaction):
        """Play/Pause gomb callback"""
        # Ellenőrizzük, hogy a felhasználó hangcsatornában van-e
        if not interaction.user.voice:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nem vagy hangcsatornában! Csatlakozz egy hangcsatornához először!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Ellenőrizzük, hogy a bot hangcsatornában van-e
        guild_id = interaction.guild_id
        if guild_id not in self.music_player.voice_clients:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="A bot nincs hangcsatornában! Használd a `/music join` parancsot!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Ellenőrizzük, hogy van-e zene a várólistában
        if guild_id not in self.music_player.queues or not self.music_player.queues[guild_id]:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="Nincs zene a várólistában! Használd a `/music play` parancsot!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Play/Pause logika
        voice_client = self.music_player.voice_clients[guild_id]
        if voice_client.is_playing():
            # Ha játszik, akkor szüneteltetjük
            await self.music_player.pause(interaction)
            self.play_pause_button.label = "▶️ Folytatás"
            self.play_pause_button.emoji = "▶️"
        else:
            # Ha szünetel, akkor folytatjuk
            await self.music_player.resume(interaction)
            self.play_pause_button.label = "⏸️ Szünet"
            self.play_pause_button.emoji = "⏸️"
        
        # Gomb frissítése
        await interaction.response.edit_message(view=self)
    
    async def stop_callback(self, interaction: discord.Interaction):
        """Stop gomb callback"""
        await self.music_player.stop(interaction)
        # Gomb visszaállítása
        self.play_pause_button.label = "▶️ Lejátszás"
        self.play_pause_button.emoji = "▶️"
        await interaction.response.edit_message(view=self)
    
    async def skip_callback(self, interaction: discord.Interaction):
        """Skip gomb callback"""
        await self.music_player.skip(interaction)
    
    async def volume_down_callback(self, interaction: discord.Interaction):
        """Volume down gomb callback"""
        guild_id = interaction.guild_id
        if guild_id in self.music_player.voice_clients:
            voice_client = self.music_player.voice_clients[guild_id]
            current_volume = voice_client.source.volume if hasattr(voice_client.source, 'volume') else 1.0
            new_volume = max(0.0, current_volume - 0.1)
            
            if hasattr(voice_client.source, 'volume'):
                voice_client.source.volume = new_volume
            
            embed = discord.Embed(
                title="🔉 Hangerej csökkentve",
                description=f"Új hangerej: {int(new_volume * 100)}%",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="A bot nincs hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def volume_up_callback(self, interaction: discord.Interaction):
        """Volume up gomb callback"""
        guild_id = interaction.guild_id
        if guild_id in self.music_player.voice_clients:
            voice_client = self.music_player.voice_clients[guild_id]
            current_volume = voice_client.source.volume if hasattr(voice_client.source, 'volume') else 1.0
            new_volume = min(2.0, current_volume + 0.1)
            
            if hasattr(voice_client.source, 'volume'):
                voice_client.source.volume = new_volume
            
            embed = discord.Embed(
                title="🔊 Hangerej növelve",
                description=f"Új hangerej: {int(new_volume * 100)}%",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Hiba!",
                description="A bot nincs hangcsatornában!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class MusicCommands(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="music", description="Zene lejátszás parancsok")
        self.bot = bot
        self.music_player = MusicPlayer(bot)
    
    @app_commands.command(name="join", description="Csatlakozás a hangcsatornához")
    async def join(self, interaction: discord.Interaction):
        """Csatlakozás a hangcsatornához"""
        await self.music_player.join_voice_channel(interaction)
    
    @app_commands.command(name="leave", description="Kilépés a hangcsatornából")
    async def leave(self, interaction: discord.Interaction):
        """Kilépés a hangcsatornából"""
        await self.music_player.leave_voice_channel(interaction)
    
    @app_commands.command(name="play", description="YouTube zene lejátszása")
    @app_commands.describe(query="YouTube URL vagy keresési kifejezés")
    async def play(self, interaction: discord.Interaction, query: str):
        """YouTube zene lejátszása"""
        # Zene hozzáadása a várólistához
        await self.music_player.add_to_queue(interaction, query)
        
        # Gombok megjelenítése
        view = MusicControlView(self.music_player)
        embed = discord.Embed(
            title="🎵 Zene Kontroll Panel",
            description="Használd a gombokat a zene vezérléséhez!",
            color=0x0099ff
        )
        embed.add_field(
            name="▶️ Lejátszás/Szünet",
            value="Zene lejátszása vagy szüneteltetése",
            inline=True
        )
        embed.add_field(
            name="⏹️ Leállítás",
            value="Zene teljes leállítása",
            inline=True
        )
        embed.add_field(
            name="⏭️ Következő",
            value="Következő számra ugrás",
            inline=True
        )
        embed.add_field(
            name="🔉🔊 Hangerej",
            value="Hangerej csökkentése/növelése",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, view=view)
    
    @app_commands.command(name="skip", description="Következő szám")
    async def skip(self, interaction: discord.Interaction):
        """Következő szám"""
        await self.music_player.skip(interaction)
    
    @app_commands.command(name="pause", description="Szüneteltetés")
    async def pause(self, interaction: discord.Interaction):
        """Szüneteltetés"""
        await self.music_player.pause(interaction)
    
    @app_commands.command(name="resume", description="Folytatás")
    async def resume(self, interaction: discord.Interaction):
        """Folytatás"""
        await self.music_player.resume(interaction)
    
    @app_commands.command(name="stop", description="Leállítás")
    async def stop(self, interaction: discord.Interaction):
        """Leállítás"""
        await self.music_player.stop(interaction)
    
    @app_commands.command(name="volume", description="Hangerej beállítása")
    @app_commands.describe(volume="Hangerej (0-100)")
    async def volume(self, interaction: discord.Interaction, volume: int):
        """Hangerej beállítása"""
        await self.music_player.set_volume(interaction, volume)
    
    @app_commands.command(name="queue", description="Várólista megjelenítése")
    async def queue(self, interaction: discord.Interaction):
        """Várólista megjelenítése"""
        await self.music_player.show_queue(interaction)
    
    @app_commands.command(name="nowplaying", description="Aktuális szám")
    async def nowplaying(self, interaction: discord.Interaction):
        """Aktuális szám"""
        # Először ellenőrizzük, hogy van-e zene
        if not await self.music_player.show_now_playing(interaction):
            return  # Ha nincs zene, a metódus már küldött hibaüzenetet
        
        # Ha van zene, megjelenítjük a gombokat
        view = MusicControlView(self.music_player)
        
        # Az aktuális szám információit is megjelenítjük
        guild_id = interaction.guild_id
        if guild_id in self.music_player.now_playing:
            now_playing = self.music_player.now_playing[guild_id]
            
            embed = discord.Embed(
                title="🎵 Most játszik",
                description=f"**{now_playing['title']}**",
                color=0x0099ff
            )
            
            if now_playing.get('thumbnail'):
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
            source_type = "🎵 Spotify" if 'spotify' in str(now_playing.get('type', '')).lower() else "📺 YouTube"
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
            
            # Gombok hozzáadása
            embed.add_field(
                name="🎮 Zene Vezérlés",
                value="Használd a gombokat a zene vezérléséhez!",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, view=view)
        else:
            # Ha valami miatt nincs now_playing, akkor csak a gombokat jelenítjük meg
            view = MusicControlView(self.music_player)
            embed = discord.Embed(
                title="🎵 Zene Kontroll Panel",
                description="Használd a gombokat a zene vezérléséhez!",
                color=0x0099ff
            )
            embed.add_field(
                name="▶️ Lejátszás/Szünet",
                value="Zene lejátszása vagy szüneteltetése",
                inline=True
            )
            embed.add_field(
                name="⏹️ Leállítás",
                value="Zene teljes leállítása",
                inline=True
            )
            embed.add_field(
                name="⏭️ Következő",
                value="Következő számra ugrás",
                inline=True
            )
            embed.add_field(
                name="🔉🔊 Hangerej",
                value="Hangerej csökkentése/növelése",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="clear", description="Várólista törlése")
    async def clear(self, interaction: discord.Interaction):
        """Várólista törlése"""
        await self.music_player.clear_queue(interaction)
    
    @app_commands.command(name="controls", description="Zene vezérlő gombok megjelenítése")
    async def controls(self, interaction: discord.Interaction):
        """Zene vezérlő gombok megjelenítése"""
        view = MusicControlView(self.music_player)
        embed = discord.Embed(
            title="🎵 Zene Kontroll Panel",
            description="Használd a gombokat a zene vezérléséhez!",
            color=0x0099ff
        )
        embed.add_field(
            name="▶️ Lejátszás/Szünet",
            value="Zene lejátszása vagy szüneteltetése",
            inline=True
        )
        embed.add_field(
            name="⏹️ Leállítás",
            value="Zene teljes leállítása",
            inline=True
        )
        embed.add_field(
            name="⏭️ Következő",
            value="Következő számra ugrás",
            inline=True
        )
        embed.add_field(
            name="🔉🔊 Hangerej",
            value="Hangerej csökkentése/növelése",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, view=view)

class HelpCommands(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="help", description="Segítség parancsok")
        self.bot = bot
    
    @app_commands.command(name="help", description="Segítség megjelenítése")
    async def help(self, interaction: discord.Interaction):
        """Segítség megjelenítése"""
        embed = discord.Embed(
            title="🎵 Discord Zene Bot - Segítség",
            description="Itt találod az összes elérhető parancsot!",
            color=0x0099ff
        )
        
        embed.add_field(
            name="🎵 Zene parancsok",
            value=(
                "`/music join` - Csatlakozás a hangcsatornához\n"
                "`/music leave` - Kilépés a hangcsatornából\n"
                "`/music play <query>` - YouTube zene lejátszása\n"
                "`/music skip` - Következő szám\n"
                "`/music pause` - Szüneteltetés\n"
                "`/music resume` - Folytatás\n"
                "`/music stop` - Leállítás\n"
                "`/music volume <0-100>` - Hangerej beállítása"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📋 Várólista parancsok",
            value=(
                "`/music queue` - Várólista megjelenítése\n"
                "`/music nowplaying` - Aktuális szám\n"
                "`/music clear` - Várólista törlése"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎮 Gomb vezérlés",
            value="`/music controls` - Zene vezérlő gombok megjelenítése",
            inline=False
        )
        
        embed.add_field(
            name="❓ Segítség",
            value="`/help help` - Ez a segítség",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tippek",
            value=(
                "• Először használd a `/music join` parancsot!\n"
                "• A `/music play` parancs YouTube URL-eket és kereséseket is elfogad\n"
                "• **Spotify támogatás:** Spotify linkeket is használhatsz!\n"
                "• DRM védett videók nem támogatottak\n"
                "• Élő adások nem támogatottak"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎵 Spotify támogatás",
            value=(
                "• **Track linkek:** `open.spotify.com/track/...`\n"
                "• **Album linkek:** `open.spotify.com/album/...`\n"
                "• **Playlist linkek:** `open.spotify.com/playlist/...`\n"
                "• **Keresés:** `spotify:track:...` vagy `spotify:album:...`\n"
                "• A bot automatikusan megtalálja a YouTube verziót!"
            ),
            inline=False
        )
        
        embed.set_footer(text="🎵 Jó zenélést!")
        
        await interaction.response.send_message(embed=embed)

def setup(bot):
    """Bot parancsok betöltése"""
    bot.tree.add_command(MusicCommands(bot))
    bot.tree.add_command(HelpCommands(bot))
