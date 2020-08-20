
import random

from .utils import Tools, Status, TimeUtils
from .htkt import Hitokoto
from .sign import SignIn
from .config import RESOURCES_BASE_PATH
from .config import commandList, hitokotoOpen, noHitokoto, highQuality



async def mainProgram(msg, bot, userQQ, userGroup, nickname, gid, uid):
    # Matching method one
    exactMatch = Tools.commandMatch(msg, commandList)
    if exactMatch:
        avatarUrl = await bot.get_channel_user_info(gid = gid, uid = uid)
        avatarUrl = avatarUrl['user']['avatar_url']
        if not avatarUrl: return
        result = await processing(userQQ, nickname, avatarUrl)
        if result == Status.FAILURE:
            return
        await bot.send_image(
                cid = userGroup,
                file_path = result,
                at_user = userQQ
            )
        return

async def processing(userQQ, nickname, avatarUrl):
    # Check if you can sign in
    result = await confirmSignIn(userQQ)
    if result == Status.FAILURE:
        return Status.FAILURE
    # Start getting hitokoto
    if hitokotoOpen:
        hitokoto = await Hitokoto.hitokoto()
    else:
        hitokoto = noHitokoto
    # Start drawing
    userInfo = await getUserInfo(userQQ)
    result = await generatePicture(userQQ, nickname, userInfo.favorability, userInfo.days, hitokoto, avatarUrl)
    if result == Status.FAILURE:
        return Status.FAILURE
    return result


async def confirmSignIn(userQQ):
    dir = f'{RESOURCES_BASE_PATH}/user'
    path = f'{RESOURCES_BASE_PATH}/user/{userQQ}.json'
    Tools.checkFolder(dir)
    content = await Tools.readJsonFile(path)
    if content == Status.FAILURE:
        basiclyConstruct = {
            'days': 1,
            'last_time': TimeUtils.getTheCurrentTime(),
            'favorability': randomFavorability(0)
        }
        await Tools.writeJsonFile(path, basiclyConstruct)
        return Status.SUCCESS
    lastTime = content['last_time']
    if TimeUtils.getTimeDifference(lastTime, model = TimeUtils.DAY) >= 1:
        content['last_time'] = TimeUtils.getTheCurrentTime()
        content['days'] += 1
        content['favorability'] = randomFavorability(content['favorability'])
        await Tools.writeJsonFile(path, content)
        return Status.SUCCESS
    return Status.FAILURE

def randomFavorability(original):
    return str(int(original) + random.randint(10, 30))


async def getUserInfo(userQQ):
    path = f'{RESOURCES_BASE_PATH}/user/{userQQ}.json'
    content = await Tools.readJsonFile(path)
    if content == Status.FAILURE:
        raise Exception(f'读取不到 {path} ！')
    return Tools.dictToObj(content)


async def generatePicture(userQQ, nickname, favorability, days, hitokoto, avatarUrl):
    result = await SignIn(userQQ, nickname, favorability, days, hitokoto, avatarUrl).drawing()
    if result == Status.FAILURE:
        return result
    if highQuality:
        path = f'{RESOURCES_BASE_PATH}/cache/{userQQ}.png'
    else:
        path = f'{RESOURCES_BASE_PATH}/cache/{userQQ}.jpg'
    return path