
from aiotomon import get_bot

from .main import handlingMessages

bot = get_bot()


@bot.on_message
async def _(ctx):
    print(f'收到了来自 [{ctx.author.name}] 的消息：{ctx.content}')
    await handlingMessages(ctx.content, bot, ctx.channel_id, ctx.author.id)