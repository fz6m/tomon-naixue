
from aiotomon import get_bot

from .main import match

bot = get_bot()

@bot.on_message
async def _(ctx):

    await match(ctx.content, bot, 
                gid = ctx.guild_id,
                cid = ctx.channel_id)
