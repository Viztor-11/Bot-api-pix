from discord.ui import View

from views.plataforma_select import PlataformaSelect

class PlataformaView(View):

    def __init__(self, modo, user):

        super().__init__()

        self.add_item(
            PlataformaSelect(
                modo,
                user
            )
        )