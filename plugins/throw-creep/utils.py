
import os
import re
import aiofiles
import aiohttp
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
    def random(items):
        return random.choice(items)


    class Dict(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__

    @classmethod
    def dictToObj(cls, dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        d = cls.Dict()
        for k, v in dictObj.items():
            d[k] = cls.dictToObj(v)
        return d

    @staticmethod
    def identifyAt(msg):
        result = re.search('<@(\d+)>', msg)
        if result:
            return result.group(1)
        return Status.FAILURE



class Network():

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    @classmethod
    async def getBytes(cls, url, headers = '', timeout = 10):
        if headers == '':
            headers = cls.DEFAULT_HEADERS
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url = url, headers = headers, timeout = timeout) as res:
                    result = await res.read()
                    return result
        except:
            return Status.FAILURE