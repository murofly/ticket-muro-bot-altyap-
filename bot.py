import os
import random
import re
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


# Intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = False


class MuroDestekBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents)

    async def setup_hook(self) -> None:
        # Global command sync
        await self.tree.sync()


bot = MuroDestekBot()


def generate_ticket_suffix() -> str:
    return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"


class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Destek Aç", style=discord.ButtonStyle.primary, custom_id="ticket_open_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        assert guild is not None

        # Create a new text channel under same category if possible
        parent = interaction.channel.category if isinstance(interaction.channel, discord.TextChannel) else None
        suffix = generate_ticket_suffix()
        channel_name = f"ticket-{suffix}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        channel = await guild.create_text_channel(name=channel_name, category=parent, overwrites=overwrites, reason="Yeni destek talebi")

        # Mention everyone and post starter message
        await channel.send(content=f"@everyone Destek talebi açıldı: {channel.mention}")

        view = TicketCloseView()
        await channel.send(
            content=f"Destek oluşturuldu. Kapatmak için 'Close' butonunu kullanın.",
            view=view,
        )

        await interaction.response.send_message(f"Yeni ticket oluşturuldu: {channel.mention}", ephemeral=True)


class TicketCloseModal(discord.ui.Modal, title="Ticket Kapatma"):
    reason = discord.ui.TextInput(label="Neden kapatıyorsunuz?", placeholder="En az 5 harf...", min_length=5, max_length=200)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Bu işlem bir metin kanalında yapılmalı.", ephemeral=True)
            return

        reason_text = str(self.reason).strip()
        if len(re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]", reason_text)) < 5:
            await interaction.response.send_message("Lütfen en az 5 harf içeren bir neden yazın.", ephemeral=True)
            return

        # Lock channel and rename
        try:
            await channel.edit(name=f"closed-{channel.name}")
        except discord.HTTPException:
            pass

        try:
            await channel.set_permissions(channel.guild.default_role, send_messages=False)
        except discord.HTTPException:
            pass

        await interaction.response.send_message(f"Ticket kapatıldı. Neden: {reason_text}")


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="ticket_close_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketCloseModal())


@bot.event
async def on_ready():
    print(f"Bot olarak giriş yapıldı: {bot.user}")
    # Persist views across restarts
    bot.add_view(TicketOpenView())
    bot.add_view(TicketCloseView())


@bot.tree.command(name="destek", description="Muro Destek komutu")
@app_commands.describe(aksiyon="ac yazarak bu kanalda destek açma mesajı gönder")
async def destek(interaction: discord.Interaction, aksiyon: str):
    if aksiyon.lower() not in {"ac", "aç"}:
        await interaction.response.send_message("Kullanım: /destek ac", ephemeral=True)
        return

    view = TicketOpenView()
    await interaction.response.send_message("Bu kanal artık destek açma kanalıdır.")
    await interaction.channel.send(content="Destek talebi açmak için aşağıdaki butona tıklayın.", view=view)


def main():
    token: Optional[str] = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN ortam değişkeni ayarlanmalı")

    bot.run(token)


if __name__ == "__main__":
    main()


