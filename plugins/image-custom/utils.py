
import os
import aiofiles
from enum import Enum

try:
    import ujson as json
except:
    import json


class Model(Enum):
    
    ALL = '_all'

    BLURRY = '_blurry'

    SEND_AT = '_send_at'

    SEND_DEFAULT = '_send_default'


class Status(Enum):

    SUCCESS = '_success'

    FAILURE = '_failure'



class Tools():

    @staticmethod
    def commandMatch(msg, commandList, model = Model.ALL):
        if model == Model.ALL:
            for c in commandList:
                if c == msg:
                    return True
        if model == Model.BLURRY:
            for c in commandList:
                if msg.find(c) != -1:
                    return True
        return False

    @staticmethod
    def checkFolder(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    async def readJsonFile(p):
        if not os.path.exists(p):
            return Status.FAILURE
        async with aiofiles.open(p, 'r', encoding='utf-8') as f:
            content = await f.read()
        return json.loads(content)


    @staticmethod
    async def writeJsonFile(p, content):
        async with aiofiles.open(p, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(content))
        return Status.SUCCESS


    @staticmethod
    async def readFileByLine(p):
        if not os.path.exists(p):
            return Status.FAILURE
        async with aiofiles.open(p, 'r', encoding = 'utf-8') as f:
            content = await f.readlines()
        return content


    @staticmethod
    async def readFileContent(p):
        if not os.path.exists(p):
            return Status.FAILURE
        async with aiofiles.open(p, 'r', encoding = 'utf-8') as f:
            content = await f.read()
        return content.strip()
    
    
    @staticmethod
    async def writeFile(p, content):
        async with aiofiles.open(p, 'w', encoding = 'utf-8') as f:
            await f.write(content)