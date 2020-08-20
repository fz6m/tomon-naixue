
import os
import random
import datetime
import aiofiles
from enum import Enum

from dateutil.parser import parse

import aiohttp

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


class TimeUtils():

    DAY = 'day'

    HOUR = 'hour'

    MINUTE = 'minute'

    SECOND = 'second'

    ALL = 'all'

    @staticmethod
    def getTheCurrentTime():
        nowDate = str(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d'))
        return nowDate

    @staticmethod
    def getAccurateTimeNow():
        nowDate = str(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d/%H:%M:%S'))
        return nowDate

    @classmethod
    def judgeTimeDifference(cls, lastTime):
        timeNow = cls.getAccurateTimeNow()
        a = parse(lastTime)
        b = parse(timeNow)
        return int((b - a).total_seconds() / 3600)

    @staticmethod
    def getTheCurrentHour():
        return int(str(datetime.datetime.strftime(datetime.datetime.now(),'%H')))

    @classmethod
    def calculateTheElapsedTimeCombination(cls, lastTime):
        timeNow = cls.getAccurateTimeNow()
        a = parse(lastTime)
        b = parse(timeNow)
        seconds = int((b - a).total_seconds())
        return [int(seconds / 3600), int((seconds % 3600) / 60), int(seconds % 60)]

    @staticmethod
    def replaceHourMinuteAndSecond(parameterList, msg):
        return (msg.replace(r'{hour}', str(parameterList[0]))
                    .replace(r'{minute}', str(parameterList[1]))
                    .replace(r'{second}', str(parameterList[2])))

    @classmethod
    def getTimeDifference(cls, original, model):
        a = parse(original)
        b = parse(cls.getAccurateTimeNow())
        seconds = int((b - a).total_seconds())
        if model == cls.ALL:
            return {
                cls.DAY: int((b - a).days),
                cls.HOUR: int(seconds / 3600),
                cls.MINUTE: int((seconds % 3600) / 60), # The rest
                cls.SECOND: int(seconds % 60) # The rest
            }
        if model == cls.DAY:
            b = parse(cls.getTheCurrentTime())
            return int((b - a).days)
        if model == cls.MINUTE:
            return int(seconds / 60)
        if model == cls.SECOND:
            return seconds



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

    @classmethod
    async def getJson(cls, url, headers = '', timeout = 10):
        if headers == '':
            headers = cls.DEFAULT_HEADERS
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url = url, headers = headers, timeout = timeout) as res:
                    result = await res.json()
                    return result
        except:
            return Status.FAILURE