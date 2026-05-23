import discord

from discord.ui import Select

from views.valor_modal import ValorModal

class PlataformaSelect(Select):

    def __init__(self, modo, user):

        super().__init__(
            placeholder="Escolha plataforma",
            options=[
                discord.SelectOption(
                    label="Mobile"
                ),

                discord.SelectOption(
                    label="Emulador"
                ),

                discord.SelectOption(
                    label="Ambos"
                )
            ]
        )

        self.modo = modo
        self.user = user

    async def callback(self, interaction):

        await interaction.response.send_modal(
            ValorModal(
                self.modo,
                self.values[0],
                self.user
            )
        )