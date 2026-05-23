import discord

from discord.ui import View

from views.plataforma_view import PlataformaView

class CriarView(View):

    @discord.ui.button(label="1v1")
    async def b1(self, interaction, button):

        await interaction.response.send_message(
            "Plataforma:",
            view=PlataformaView(
                "1v1",
                interaction.user
            ),
            ephemeral=True
        )

    @discord.ui.button(label="2v2")
    async def b2(self, interaction, button):

        await interaction.response.send_message(
            "Plataforma:",
            view=PlataformaView(
                "2v2",
                interaction.user
            ),
            ephemeral=True
        )

    @discord.ui.button(label="3v3")
    async def b3(self, interaction, button):

        await interaction.response.send_message(
            "Plataforma:",
            view=PlataformaView(
                "3v3",
                interaction.user
            ),
            ephemeral=True
        )

    @discord.ui.button(label="4v4")
    async def b4(self, interaction, button):

        await interaction.response.send_message(
            "Plataforma:",
            view=PlataformaView(
                "4v4",
                interaction.user
            ),
            ephemeral=True
        )