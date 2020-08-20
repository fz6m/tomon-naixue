
from aiotomon import get_bot

from .main import mainProgram

bot = get_bot()

@bot.on_message
async def _(ctx):
    
    await mainProgram(bot, ctx.author.id, ctx.guild_id, 
                        ctx.content, ctx.author.name, ctx.channel_id)