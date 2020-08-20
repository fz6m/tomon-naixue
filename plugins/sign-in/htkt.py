
import os

from .config import RESOURCES_BASE_PATH
from .config import hitokotoBlacklist, hitokotoArchiveOpen, noHitokoto

from .utils import Status, Tools, Network, Model


class Hitokoto():

    BASE_PATH = 'https://v1.hitokoto.cn/'

    ARCHIVE_PATH = f'{RESOURCES_BASE_PATH}/hitokoto/cache/archive.json'

    ARCHIVE_FOLDER = f'{RESOURCES_BASE_PATH}/hitokoto/cache'

    @classmethod
    async def retrieveLocalArchive(cls):
        path = cls.ARCHIVE_PATH
        if not os.path.exists(path): return Status.FAILURE
        return Tools.random(await Tools.readJsonFile(path)['list'])

    @classmethod
    async def get(cls):
        result = await Network.getJson(url = cls.BASE_PATH)
        # Retrieve failed, start to retrieve local archive
        if result == Status.FAILURE:
            return await cls.retrieveLocalArchive()
        # Check blacklist
        hitokoto = result['hitokoto']
        if Tools.commandMatch(hitokoto, hitokotoBlacklist, Model.BLURRY):
            # Retry only once
            result = await Network.getJson(url = cls.BASE_PATH)
            if result == Status.FAILURE:
                return await cls.retrieveLocalArchive()
            hitokoto = result['hitokoto']
            if Tools.commandMatch(hitokoto, hitokotoBlacklist, Model.BLURRY):
                return Status.FAILURE
        # Archive
        await cls.archive(hitokoto)
        return hitokoto
            
    @classmethod
    async def archive(cls, content):
        if not hitokotoArchiveOpen:
            return
        Tools.checkFolder(cls.ARCHIVE_FOLDER)
        path = cls.ARCHIVE_PATH
        if not os.path.exists(path):
            basiclyConstruct = {
                'list': [content],
                'count': 1
            }
            await Tools.writeJsonFile(path, basiclyConstruct)
            return
        fileContent = await Tools.readJsonFile(path)
        fileContent['list'].append(content)
        fileContent['count'] += 1
        await Tools.writeJsonFile(path, fileContent)
        return

    @classmethod
    async def hitokoto(cls):
        result = await cls.get()
        if result == Status.FAILURE:
            return noHitokoto
        return result