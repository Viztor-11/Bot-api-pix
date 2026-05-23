async def log(bot, guild, channel_id, msg):
    try:
        canal = bot.get_channel(channel_id)

        if canal:
            await canal.send(msg)

    except Exception as e:
        print("ERRO LOG:", e)