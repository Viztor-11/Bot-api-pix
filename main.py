import discord

from discord.ext import commands

from config import TOKEN

from views.criar_view import CriarView

GUILD_ID = 1489812219368837220

guild = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.tree.command(
    name="aposta",
    description="Criar aposta",
    guild=guild
)
async def aposta(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(
            "Escolha o modo:",
            view=CriarView(),
            ephemeral=True
        )

    except Exception as e:
        print("ERRO NO COMANDO /aposta:", e)

@bot.event
async def setup_hook():

    synced = await bot.tree.sync(
        guild=guild
    )

    print(
        f"{len(synced)} comandos sincronizados"
    )

@bot.event
async def on_ready():

    print(
        f"Bot online: {bot.user}"
    )

bot.run(TOKEN)