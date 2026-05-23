import discord
import uuid

from discord.ui import Modal, TextInput

from data import apostas
from data import usuarios_em_aposta

from views.aposta_view import ApostaView

class ValorModal(Modal):

    def __init__(self, modo, plataforma, user):

        super().__init__(title="Valor")

        self.modo = modo
        self.plataforma = plataforma
        self.user = user

        self.valor = TextInput(
            label="Valor"
        )

        self.add_item(self.valor)

    async def on_submit(self, interaction):

        if self.user.id in usuarios_em_aposta:

            return await interaction.response.send_message(
                "Você já está em uma aposta!",
                ephemeral=True
            )

        valor = float(
            self.valor.value.replace(",", ".")
        )

        aposta_id = str(uuid.uuid4())[:6]

        apostas[aposta_id] = {
            "criador": self.user.id,
            "valor": valor,
            "modo": self.modo,
            "plataforma": self.plataforma,
            "oponente": None
        }

        usuarios_em_aposta.add(
            self.user.id
        )

        embed = discord.Embed(
            title="🎯 Nova aposta",
            color=0x00ff00
        )

        embed.add_field(
            name="Modo",
            value=self.modo
        )

        embed.add_field(
            name="Plataforma",
            value=self.plataforma
        )

        embed.add_field(
            name="Valor",
            value=f"R${valor:.2f}"
        )

        embed.add_field(
            name="Prêmio",
            value=f"R${round(valor*2*0.88,2):.2f}"
        )

        await interaction.response.send_message(
            "Criado!",
            ephemeral=True
        )

        await interaction.channel.send(
            embed=embed,
            view=ApostaView(aposta_id)
        )