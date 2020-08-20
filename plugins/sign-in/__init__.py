
from aiotomon import get_bot

from .main import mainProgram

bot = get_bot()

@bot.on_message
async def _(ctx):

    await mainProgram(ctx.content, bot, ctx.author.id, 
                      ctx.channel_id, ctx.author.name, 
                      ctx.guild_id, ctx.author.id)
