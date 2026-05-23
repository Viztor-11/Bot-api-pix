import discord

from config import MOD_ROLE_ID
from data import apostas
from views.partida_view import PartidaView


async def criar_sala(interaction, aposta_id):
    aposta = apostas[aposta_id]

    guild = interaction.guild
    criador = await guild.fetch_member(aposta["criador"])
    oponente = await guild.fetch_member(aposta["oponente"])

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        criador: discord.PermissionOverwrite(read_messages=True),
        oponente: discord.PermissionOverwrite(read_messages=True),
        guild.self_member: discord.PermissionOverwrite(read_messages=True)
    }

    canal = await guild.create_text_channel(
        name=f"aposta-{criador.name}",
        overwrites=overwrites
    )

    aposta["canal"] = canal.id

    embed = discord.Embed(title="Sala criada", color=0x00ff00)
    embed.description = f"{criador.mention} vs {oponente.mention}"

    embed.add_field(name="Modo", value=aposta["modo"])
    embed.add_field(name="Plataforma", value=aposta["plataforma"])
    embed.add_field(name="Valor", value=f"R${aposta['valor']:.2f}")
    embed.add_field(name="Prêmio", value=f"R${round(aposta['valor'] * 2 * 0.88, 2):.2f}")

    cargo = guild.get_role(MOD_ROLE_ID)

    mensagem = f"{cargo.mention} nova partida!" if cargo else "Nova partida criada."

    await canal.send(
        content=mensagem,
        embed=embed,
        view=PartidaView(aposta_id, criador, oponente)
    )