import discord
import asyncio

from discord.ui import View, Button

from data import apostas
from data import usuarios_em_aposta

from services.pix import criar_pix
from services.pix import gerar_qr

class PartidaView(View):

    def __init__(self, aposta_id, criador, oponente):
        super().__init__(timeout=None)

        self.id = aposta_id
        self.criador = criador
        self.oponente = oponente

        self.confirmados = set()

        self.mod = False
        self.finalizada = False

    # ================= CONFIRMAR =================

    @discord.ui.button(label="Confirmar Jogador")
    async def confirmar(self, interaction, button):

        aposta = apostas[self.id]

        if interaction.user.id not in [
            aposta["criador"],
            aposta["oponente"]
        ]:

            return await interaction.response.send_message(
                "Você não participa!",
                ephemeral=True
            )

        if interaction.user.id in self.confirmados:

            return await interaction.response.send_message(
                "Você já confirmou!",
                ephemeral=True
            )

        self.confirmados.add(interaction.user.id)

        await interaction.response.defer()

        await interaction.channel.send(
            f"{interaction.user.mention} confirmou!"
        )

        if len(self.confirmados) == 2 and self.mod:

            await self.enviar_pix(interaction)

    # ================= MOD =================

    @discord.ui.button(label="Confirmar Moderador")
    async def confirmar_mod(self, interaction, button):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Apenas moderador!",
                ephemeral=True
            )

        if self.mod:

            return await interaction.response.send_message(
                "Moderador já confirmou!",
                ephemeral=True
            )

        self.mod = True

        await interaction.response.defer()

        await interaction.channel.send(
            f"Moderador {interaction.user.mention} confirmou!"
        )

        if len(self.confirmados) == 2:

            await self.enviar_pix(interaction)

    # ================= PIX =================

    async def enviar_pix(self, interaction):

        aposta = apostas[self.id]

        criador = await interaction.guild.fetch_member(
            aposta["criador"]
        )

        oponente = await interaction.guild.fetch_member(
            aposta["oponente"]
        )

        p1 = criar_pix(
            criador.id,
            self.id,
            aposta["valor"]
        )

        p2 = criar_pix(
            oponente.id,
            self.id,
            aposta["valor"]
        )

        if not p1 or not p2:

            return await interaction.channel.send(
                "Erro ao gerar PIX!"
            )

        d1 = p1["point_of_interaction"]["transaction_data"]
        d2 = p2["point_of_interaction"]["transaction_data"]

        await interaction.channel.send(
            f"{criador.mention} pague:",
            file=gerar_qr(d1["qr_code_base64"])
        )

        await interaction.channel.send(
            d1["ticket_url"]
        )

        await interaction.channel.send(
            f"{oponente.mention} pague:",
            file=gerar_qr(d2["qr_code_base64"])
        )

        await interaction.channel.send(
            d2["ticket_url"]
        )

        await interaction.channel.send(
            "5 minutos para pagar!"
        )

    # ================= FINALIZAR =================

    @discord.ui.button(
        label="🏆 Definir vencedor",
        style=discord.ButtonStyle.green
    )
    async def vencedor(self, interaction, button):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Apenas moderador!",
                ephemeral=True
            )

        await interaction.response.defer()

        view = View()

        async def v1(i):

            await self.finalizar(
                i,
                self.criador,
                self.oponente
            )

        async def v2(i):

            await self.finalizar(
                i,
                self.oponente,
                self.criador
            )

        b1 = Button(
            label=f"{self.criador.display_name} 🏆",
            style=discord.ButtonStyle.green
        )

        b2 = Button(
            label=f"{self.oponente.display_name} 🏆",
            style=discord.ButtonStyle.green
        )

        b1.callback = v1
        b2.callback = v2

        view.add_item(b1)
        view.add_item(b2)

        await interaction.followup.send(
            "Escolha o vencedor:",
            view=view
        )

    async def finalizar(self, interaction, vencedor, perdedor):

        if self.finalizada:

            return await interaction.response.send_message(
                "Já finalizado!",
                ephemeral=True
            )

        self.finalizada = True

        await interaction.response.defer()

        await interaction.channel.send(
            f"{vencedor.mention} venceu!\n"
            f"{perdedor.mention} perdeu!"
        )

    # ================= FECHAR =================

    @discord.ui.button(
        label="🗑️ Fechar Sala",
        style=discord.ButtonStyle.red
    )
    async def fechar(self, interaction, button):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Apenas moderador!",
                ephemeral=True
            )

        await interaction.response.defer()

        aposta = apostas[self.id]

        usuarios_em_aposta.discard(
            aposta["criador"]
        )

        usuarios_em_aposta.discard(
            aposta["oponente"]
        )

        apostas.pop(self.id, None)

        await interaction.channel.delete()