
import os
import random
import aiofiles
from enum import Enum

import datetime
from dateutil.parser import parse

try:
    import ujson as json
except:
    import json

from .config import RESOURCES_BASE_PATH

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

    @staticmethod
    def at(user):
        return f'<@{user}>\n'


class GoodMorningModel(Enum):

    MORNING_MODEL = 'MORNING_MODEL'

    NIGHT_MODEL = 'NIGHT_MODEL'


class Utils():

    @staticmethod
    async def userInformationReading(userQQ):
        p = f'{RESOURCES_BASE_PATH}/Data/User/{userQQ}.json'
        content = await Tools.readJsonFile(p)
        return content

    @staticmethod
    async def userInformationWriting(userQQ, info):
        Tools.checkFolder(f'{RESOURCES_BASE_PATH}/Data/User')
        p = f'{RESOURCES_BASE_PATH}/Data/User/{userQQ}.json'
        await Tools.writeJsonFile(p, info)
        return Status.SUCCESS

    @staticmethod
    async def groupRead(userGroup):
        p = f'{RESOURCES_BASE_PATH}/Data/Group/{userGroup}.json'
        group = await Tools.readJsonFile(p)
        return group

    @staticmethod
    async def groupWrite(userGroup, info):
        Tools.checkFolder(f'{RESOURCES_BASE_PATH}/Data/Group')
        p = f'{RESOURCES_BASE_PATH}/Data/Group/{userGroup}.json'
        await Tools.writeJsonFile(p, info)
        return Status.SUCCESS

    @staticmethod
    async def readConfiguration(model):
        content = ''
        if model == GoodMorningModel.MORNING_MODEL.value:
            content = await Tools.readJsonFile(f'{RESOURCES_BASE_PATH}/Config/GoodMorning.json')
        if model == GoodMorningModel.NIGHT_MODEL.value:
            content = await Tools.readJsonFile(f'{RESOURCES_BASE_PATH}/Config/GoodNight.json')
        if content == Status.FAILURE:
            raise Exception('缺少早晚安配置文件！')
        return content

    @classmethod
    async def extractRandomWords(cls, model, nickname):
        return random.choice((await cls.readConfiguration(model))['statement'])['content'].replace(r'{name}', nickname)

    @classmethod
    async def extractConfigurationInformationAccordingToSpecifiedParameters(cls, parameter, model):
        return (await cls.readConfiguration(model))[parameter]


class TimeUtils():

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