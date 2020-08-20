
from aiotomon import get_bot

from .main import mainEntrance

bot = get_bot()

@bot.on_message
async def _(ctx):

    await mainEntrance(ctx.content, ctx.author.id, ctx.channel_id, bot)