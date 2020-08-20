
from .utils import Tools, Model, Status
from .config import creepCommandList, throwCommandList
from .throwcreep import ThrowAndCreep


async def match(plainText, bot, gid, cid):
    # creep features
    result = Tools.commandMatch(plainText, creepCommandList, model = Model.BLURRY)
    if result:
        # Parsing parameters
        params = Tools.identifyAt(plainText)
        if params != Status.FAILURE:

            avatarUrl = await getAvatarUrl(gid, params, bot)
            if not avatarUrl: return

            outPath = await ThrowAndCreep.creep(params, avatarUrl)

            await bot.send_image(
                cid = cid,
                file_path = outPath
            )

            return
    # throe features
    result = Tools.commandMatch(plainText, throwCommandList, model = Model.BLURRY)
    if result:
        # Parsing parameters
        params = Tools.identifyAt(plainText)
        if params != Status.FAILURE:

            avatarUrl = await getAvatarUrl(gid, params, bot)
            if not avatarUrl: return

            outPath = await ThrowAndCreep.throw(params, avatarUrl)

            await bot.send_image(
                cid = cid,
                file_path = outPath
            )

            return


async def getAvatarUrl(gid, uid, bot):
    avatarUrl = await bot.get_channel_user_info(gid = gid, uid = uid)
    avatarUrl = avatarUrl['user']['avatar_url']
    return avatarUrl
