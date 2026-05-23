import discord
from discord.ui import View

from data import apostas, usuarios_em_aposta
from services.sala import criar_sala


class ApostaView(View):
    def __init__(self, aposta_id):
        super().__init__(timeout=None)
        self.id = aposta_id

    @discord.ui.button(label="Entrar", style=discord.ButtonStyle.green)
    async def entrar(self, interaction, button):
        if interaction.user.id in usuarios_em_aposta:
            return await interaction.response.send_message(
                "Você já está em aposta!",
                ephemeral=True
            )

        aposta = apostas[self.id]
        aposta["oponente"] = interaction.user.id

        usuarios_em_aposta.add(interaction.user.id)

        await interaction.response.defer()

        await interaction.message.delete()

        await criar_sala(interaction, self.id)

    @discord.ui.button(label="Cancelar Aposta", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction, button):
        aposta = apostas[self.id]

        if interaction.user.id != aposta["criador"]:
            return await interaction.response.send_message(
                "Sem permissão!",
                ephemeral=True
            )

        usuarios_em_aposta.discard(aposta["criador"])
        apostas.pop(self.id, None)

        await interaction.message.delete()