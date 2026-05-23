

import discord
from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput
import uuid
import mercadopago
import base64
from io import BytesIO
import asyncio
from dotenv import load_dotenv
import os

# ================= CONFIG =================
load_dotenv()

TOKEN = os.getenv("TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
MOD_ROLE_ID = int(os.getenv("MOD_ROLE_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

apostas = {}
usuarios_em_aposta = set()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= LOG =================

async def log(guild, msg):
    try:
        canal = bot.get_channel(LOG_CHANNEL_ID)
        if canal:
            await canal.send(msg)
        else:
            print("❌ Canal de log não encontrado")
    except Exception as e:
        print("ERRO LOG:", e)

# ================= PIX =================

def criar_pix(user_id, aposta_id, valor):
    try:
        p = sdk.payment().create({
            "transaction_amount": float(valor),
            "description": f"Aposta {aposta_id}",
            "payment_method_id": "pix",
            "external_reference": f"{user_id}|{aposta_id}",
            "payer": {"email": "teste@teste.com"}
        })["response"]

        if "point_of_interaction" not in p:
            print(p)
            return None

        return p
    except Exception as e:
        print(e)
        return None


def gerar_qr(base64_string):
    return discord.File(BytesIO(base64.b64decode(base64_string)), filename="qr.png")

# ================= TIMEOUT =================

async def timeout_pagamento(canal, aposta_id):
    await asyncio.sleep(300)

    if aposta_id not in apostas:
        return

    aposta = apostas[aposta_id]

    if aposta.get("pago"):
        return

    await canal.send("❌ Tempo esgotado! Sala cancelada.")

    usuarios_em_aposta.discard(aposta["criador"])
    usuarios_em_aposta.discard(aposta["oponente"])

    await log(canal.guild, f"⏰ Aposta {aposta_id} cancelada por tempo")

    apostas.pop(aposta_id, None)

    await canal.delete()

# ================= SALA =================

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

    embed = discord.Embed(title="🔥 Sala Criada!", color=0x00ff00)
    embed.description = f"{criador.mention} vs {oponente.mention}"

    embed.add_field(name="Modo", value=aposta["modo"])
    embed.add_field(name="Plataforma", value=aposta["plataforma"])
    embed.add_field(name="Valor", value=f"R${aposta['valor']:.2f}")
    embed.add_field(name="Prêmio", value=f"R${round(aposta['valor']*2*0.88,2):.2f}")

    cargo = guild.get_role(MOD_ROLE_ID)

    if cargo:
        mensagem = f"{cargo.mention} nova partida!"
    else:
        mensagem = "🚨 Nova partida criada! (cargo mod não encontrado)"

    await canal.send(
        content=mensagem,
        embed=embed,
        view=PartidaView(aposta_id, criador, oponente)
    )

    await log(guild, f"📢 Nova sala: {criador} vs {oponente}")

# ================= PARTIDA =================

class PartidaView(View):
    def __init__(self, aposta_id, criador, oponente):
        super().__init__(timeout=None)
        self.id = aposta_id
        self.criador = criador
        self.oponente = oponente
        self.confirmados = set()
        self.mod = False
        self.finalizada = False

    # ================= CONFIRMAR JOGADOR =================
    @discord.ui.button(label="Confirmar Jogador")
    async def confirmar(self, interaction: discord.Interaction, button: Button):

        aposta = apostas[self.id]

        if interaction.user.id not in [aposta["criador"], aposta["oponente"]]:
            return await interaction.response.send_message("Você não participa!", ephemeral=True)

        if interaction.user.id in self.confirmados:
            return await interaction.response.send_message("Você Já Confirmou💀", ephemeral=True)

        self.confirmados.add(interaction.user.id)

        await interaction.response.defer()  # 🔥 evita erro

        await interaction.channel.send(
            f"🦈 Jogador: {interaction.user.mention} Confirmou!"
        )

        if len(self.confirmados) == 2 and self.mod:
            await enviar_pix(interaction, self.id)

    # ================= CONFIRMAR MOD =================
    @discord.ui.button(label="Confirmar Moderador")
    async def confirmar_mod(self, interaction: discord.Interaction, button: Button):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Apenas moderador!", ephemeral=True)

        if self.mod:
            return await interaction.response.send_message("Já confirmado!", ephemeral=True)

        self.mod = True

        await interaction.response.defer()  # 🔥 evita erro

        await interaction.channel.send(
            f"🦧 Moderador: {interaction.user.mention} Confirmou!"
        )

        if len(self.confirmados) == 2:
            await enviar_pix(interaction, self.id)

    # ================= DEFINIR VENCEDOR =================
    @discord.ui.button(label="🏆 Definir vencedor", style=discord.ButtonStyle.green)
    async def vencedor(self, interaction: discord.Interaction, button: Button):

        # 🔥 BLOQUEIO REAL
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ Apenas moderadores podem definir vencedor!",
                ephemeral=True
            )

        await interaction.response.defer()  # 🔥 evita erro

        view = View()

        async def v1(i):
            if not i.user.guild_permissions.administrator:
                return await i.response.send_message("❌ Apenas moderador!", ephemeral=True)
            await self.finalizar(i, self.criador, self.oponente)

        async def v2(i):
            if not i.user.guild_permissions.administrator:
                return await i.response.send_message("❌ Apenas moderador!", ephemeral=True)
            await self.finalizar(i, self.oponente, self.criador)

        b1 = Button(label=f"{self.criador.display_name} 🏆", style=discord.ButtonStyle.green)
        b2 = Button(label=f"{self.oponente.display_name} 🏆", style=discord.ButtonStyle.green)

        b1.callback = v1
        b2.callback = v2

        view.add_item(b1)
        view.add_item(b2)

        await interaction.followup.send("Escolha o vencedor:", view=view)

    # ================= FINALIZAR =================
    async def finalizar(self, interaction, vencedor, perdedor):

        if self.finalizada:
            return await interaction.response.send_message("Já finalizado!", ephemeral=True)

        self.finalizada = True

        await interaction.response.defer()

        await interaction.channel.send(
            f"{vencedor.mention} 🏆 Venceu!\n💀 {perdedor.mention} Perdeu!"
        )

        await log(interaction.guild, f"🏆 {vencedor} venceu aposta")

    # ================= FECHAR SALA =================
    @discord.ui.button(label="🗑️ Fechar Sala", style=discord.ButtonStyle.red)
    async def fechar(self, interaction: discord.Interaction, button: Button):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Apenas moderador!", ephemeral=True)

        await interaction.response.defer()

        aposta = apostas[self.id]

        usuarios_em_aposta.discard(aposta["criador"])
        usuarios_em_aposta.discard(aposta["oponente"])

        await log(interaction.guild, f"🗑️ Sala fechada {self.id}")

        apostas.pop(self.id, None)

        await interaction.channel.delete()

# ================= PIX =================

async def enviar_pix(interaction, aposta_id):
    aposta = apostas[aposta_id]

    criador = await interaction.guild.fetch_member(aposta["criador"])
    oponente = await interaction.guild.fetch_member(aposta["oponente"])

    p1 = criar_pix(criador.id, aposta_id, aposta["valor"])
    p2 = criar_pix(oponente.id, aposta_id, aposta["valor"])

    if not p1 or not p2:
        return await interaction.channel.send("❌ Erro ao gerar Pix!")

    d1 = p1["point_of_interaction"]["transaction_data"]
    d2 = p2["point_of_interaction"]["transaction_data"]

    await interaction.channel.send(f"{criador.mention} pague:", file=gerar_qr(d1["qr_code_base64"]))
    await interaction.channel.send(d1["ticket_url"])

    await interaction.channel.send(f"{oponente.mention} pague:", file=gerar_qr(d2["qr_code_base64"]))
    await interaction.channel.send(d2["ticket_url"])

    await interaction.channel.send("⏳ 5 minutos para pagar!")

    asyncio.create_task(timeout_pagamento(interaction.channel, aposta_id))

# ================= UI =================

class ValorModal(Modal):
    def __init__(self, modo, plataforma, user):
        super().__init__(title="Valor")
        self.modo = modo
        self.plataforma = plataforma
        self.user = user
        self.valor = TextInput(label="Valor")
        self.add_item(self.valor)

    async def on_submit(self, interaction):
        if self.user.id in usuarios_em_aposta:
            return await interaction.response.send_message("Você já está em uma aposta!", ephemeral=True)

        valor = float(self.valor.value.replace(",", "."))

        aposta_id = str(uuid.uuid4())[:6]

        apostas[aposta_id] = {
            "criador": self.user.id,
            "valor": valor,
            "modo": self.modo,
            "plataforma": self.plataforma,
            "oponente": None
        }

        usuarios_em_aposta.add(self.user.id)

        await log(
            interaction.guild,
            f"📌 Nova aposta por {interaction.user} | {self.modo} | R${valor}"
        )

        embed = discord.Embed(title="🎯 Nova aposta", color=0x00ff00)
        embed.add_field(name="Modo", value=self.modo)
        embed.add_field(name="Plataforma", value=self.plataforma)
        embed.add_field(name="Valor", value=f"R${valor:.2f}")
        embed.add_field(name="Prêmio", value=f"R${round(valor*2*0.88,2):.2f}")

        await interaction.response.send_message("Criado!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=ApostaView(aposta_id))

class PlataformaSelect(Select):
    def __init__(self, modo, user):
        super().__init__(
            placeholder="Escolha plataforma",
            options=[
                discord.SelectOption(label="Mobile"),
                discord.SelectOption(label="Emulador"),
                discord.SelectOption(label="Ambos")
            ]
        )
        self.modo = modo
        self.user = user

    async def callback(self, interaction):
        await interaction.response.send_modal(
            ValorModal(self.modo, self.values[0], self.user)
        )

class PlataformaView(View):
    def __init__(self, modo, user):
        super().__init__()
        self.add_item(PlataformaSelect(modo, user))

class CriarView(View):

    @discord.ui.button(label="1v1")
    async def b1(self, i, b):
        await i.response.send_message("Plataforma:", view=PlataformaView("1v1", i.user), ephemeral=True)

    @discord.ui.button(label="2v2")
    async def b2(self, i, b):
        await i.response.send_message("Plataforma:", view=PlataformaView("2v2", i.user), ephemeral=True)

    @discord.ui.button(label="3v3")
    async def b3(self, i, b):
        await i.response.send_message("Plataforma:", view=PlataformaView("3v3", i.user), ephemeral=True)

    @discord.ui.button(label="4v4")
    async def b4(self, i, b):
        await i.response.send_message("Plataforma:", view=PlataformaView("4v4", i.user), ephemeral=True)

# ================= APOSTA =================

class ApostaView(View):
    def __init__(self, aposta_id):
        super().__init__(timeout=None)
        self.id = aposta_id

    @discord.ui.button(label="Entrar", style=discord.ButtonStyle.green)
    async def entrar(self, interaction, b):
        if interaction.user.id in usuarios_em_aposta:
            return await interaction.response.send_message("Você já está em aposta!", ephemeral=True)

        aposta = apostas[self.id]
        aposta["oponente"] = interaction.user.id

        usuarios_em_aposta.add(interaction.user.id)

        await log(interaction.guild, f"⚔️ {interaction.user} entrou na aposta {self.id}")

        await interaction.message.delete()

        await criar_sala(interaction, self.id)

    @discord.ui.button(label="Cancelar Aposta", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction, b):
        aposta = apostas[self.id]

        if interaction.user.id != aposta["criador"]:
            return await interaction.response.send_message("Sem permissão!", ephemeral=True)

        usuarios_em_aposta.discard(aposta["criador"])
        apostas.pop(self.id, None)

        await interaction.message.delete()

# ================= SLASH =================

@bot.tree.command(name="aposta")
async def aposta(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🎮 Escolha o modo:",
        view=CriarView(),
        ephemeral=True
    )

# ================= READY =================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot online!")

bot.run(TOKEN)