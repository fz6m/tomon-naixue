
import random

from .config import goodMorningInstructionSet, goodNightInstructionSet
from .utils import Tools, Status, Utils, TimeUtils, GoodMorningModel


async def mainProgram(bot, userQQ, userGroup, msg, nickname, cid):
    # Good morning match
    if Tools.commandMatch(msg, goodMorningInstructionSet):
        sendMsg = await goodMorningInformation(userQQ, userGroup, nickname)

        await bot.send_text(
            cid = cid,
            content = sendMsg
        )

        return
    # Good night detection
    if Tools.commandMatch(msg, goodNightInstructionSet):
        sendMsg = await goodNightInformation(userQQ, userGroup, nickname)

        await bot.send_text(
            cid = cid,
            content = sendMsg
        )

        return

async def userRegistration(userQQ, model):
    registrationStructure = {
        'qq': userQQ,
        'model': model,
        'time': TimeUtils.getTheCurrentTime(),
        'accurateTime': TimeUtils.getAccurateTimeNow()
    }
    await Utils.userInformationWriting(userQQ, registrationStructure)
    return Status.SUCCESS


async def createACheckInPool(userGroup, model):
    signInPoolStructure = {
        'qun': userGroup,
        'time': TimeUtils.getTheCurrentTime(),
        'accurateTime': TimeUtils.getAccurateTimeNow(),
        'userList': [],
        'number': 0
    }
    await Utils.groupWrite(str(userGroup) + '-' + model, signInPoolStructure)
    return Status.SUCCESS


async def addToCheckInPoolAndGetRanking(userQQ, userGroup, model):
    if model == GoodMorningModel.MORNING_MODEL.value:
        # Check if there is a check-in pool
        content = await Utils.groupRead(str(userGroup) + '-' + model)
        if content == Status.FAILURE:
            # Create a check-in pool
            await createACheckInPool(userGroup, model)
            content = await Utils.groupRead(str(userGroup) + '-' + model)
        # Check if the pool has expired
        if content['time'] != TimeUtils.getTheCurrentTime():
            # Expired, rebuild the pool
            await createACheckInPool(userGroup, model)
            content = await Utils.groupRead(str(userGroup) + '-' + model)
        # Add users to the check-in pool
        user = await Utils.userInformationReading(userQQ)
        content['userList'].append(user)
        content['number'] += 1
        await Utils.groupWrite(str(userGroup) + '-' + model, content)
        return content['number']
    if model == GoodMorningModel.NIGHT_MODEL.value:
        # Check if there is a check-in pool
        content = await Utils.groupRead(str(userGroup) + '-' + model)
        if content == Status.FAILURE:
            # Create a check-in pool
            await createACheckInPool(userGroup, model)
            content = await Utils.groupRead(str(userGroup) + '-' + model)
        # Check if the pool has expired
        hourNow = TimeUtils.getTheCurrentHour()
        expiryId = False
        if content['time'] != TimeUtils.getTheCurrentTime():
            if TimeUtils.judgeTimeDifference(content['accurateTime']) < 24:
                if hourNow >= 12:
                    expiryId = True
            else:
                expiryId = True
        if expiryId:
            # Expired, rebuild the pool
            await createACheckInPool(userGroup, model)
            content = await Utils.groupRead(str(userGroup) + '-' + model)
        # Add users to the check-in pool
        user = await Utils.userInformationReading(userQQ)
        content['userList'].append(user)
        content['number'] += 1
        await Utils.groupWrite(str(userGroup) + '-' + model, content)
        return content['number']


async def goodMorningInformation(userQQ, userGroup, nickname):
    # Check if registered
    registered = await Utils.userInformationReading(userQQ)
    send = Tools.at(userQQ)
    if registered == Status.FAILURE:
        # registered
        await userRegistration(userQQ, GoodMorningModel.MORNING_MODEL.value)
        # Add to check-in pool and get ranking
        rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.MORNING_MODEL.value)
        send += (await Utils.extractRandomWords(GoodMorningModel.MORNING_MODEL.value, nickname) + '\n' +
                (await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.MORNING_MODEL.value)).replace(r'{number}', str(rank)))
        return send
    # Already registered
    if registered['model'] == GoodMorningModel.MORNING_MODEL.value:
        # too little time
        if TimeUtils.judgeTimeDifference(registered['accurateTime']) <= 4:
            send += await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('triggered', GoodMorningModel.MORNING_MODEL.value)
            return send
        # Good morning no twice a day
        if registered['time'] != TimeUtils.getTheCurrentTime():
            await userRegistration(userQQ, GoodMorningModel.MORNING_MODEL.value)
            rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.MORNING_MODEL.value)
            send += (await Utils.extractRandomWords(GoodMorningModel.MORNING_MODEL.value, nickname) + '\n' +
                (await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.MORNING_MODEL.value)).replace(r'{number}', str(rank)))
            return send
    if registered['model'] == GoodMorningModel.NIGHT_MODEL.value:
        sleepingTime = TimeUtils.judgeTimeDifference(registered['accurateTime'])
        # too little time
        if sleepingTime <= 4:
            send += await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('unable_to_trigger', GoodMorningModel.MORNING_MODEL.value)
            return send
        # Sleep time cannot exceed 24 hours
        await userRegistration(userQQ, GoodMorningModel.MORNING_MODEL.value)
        if sleepingTime < 24:
            send += await Utils.extractRandomWords(GoodMorningModel.MORNING_MODEL.value, nickname)
            # Calculate Wake Up Ranking
            rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.MORNING_MODEL.value)
            send += ((await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.MORNING_MODEL.value)).replace(r'{number}', str(rank)) + '\n')
            # Calculate precise sleep time
            sleepPreciseTime = TimeUtils.calculateTheElapsedTimeCombination(registered['accurateTime'])
            if sleepPreciseTime[0] >= 9:
                send += TimeUtils.replaceHourMinuteAndSecond(sleepPreciseTime, 
                            (await Utils.readConfiguration(GoodMorningModel.MORNING_MODEL.value))['sleeping_time'][1]['content'])
            elif sleepPreciseTime[0] >= 7:
                send += TimeUtils.replaceHourMinuteAndSecond(sleepPreciseTime, 
                            (await Utils.readConfiguration(GoodMorningModel.MORNING_MODEL.value))['sleeping_time'][0]['content'])
            else:
                send += TimeUtils.replaceHourMinuteAndSecond(sleepPreciseTime, 
                            (await Utils.readConfiguration(GoodMorningModel.MORNING_MODEL.value))['too_little_sleep'])
        else:
            rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.MORNING_MODEL.value)
            send += (await Utils.extractRandomWords(GoodMorningModel.MORNING_MODEL.value, nickname) + '\n' +
                (await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.MORNING_MODEL.value)).replace(r'{number}', str(rank)))
        return send
    return Status.FAILURE


async def goodNightInformation(userQQ, userGroup, nickname):
    # Check if registered
    registered = await Utils.userInformationReading(userQQ)
    send = Tools.at(userQQ)
    if registered == Status.FAILURE:
        # registered
        await userRegistration(userQQ, GoodMorningModel.NIGHT_MODEL.value)
        # Add to check-in pool and get ranking
        rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.NIGHT_MODEL.value)
        send += (await Utils.extractRandomWords(GoodMorningModel.NIGHT_MODEL.value, nickname) + '\n' +
                (await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.NIGHT_MODEL.value)).replace(r'{number}', str(rank)))
        return send
    # Already registered
    if registered['model'] == GoodMorningModel.NIGHT_MODEL.value:
        # too little time
        if TimeUtils.judgeTimeDifference(registered['accurateTime']) <= 4:
            send += await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('triggered', GoodMorningModel.NIGHT_MODEL.value)
            return send
        # Two good nights can not be less than 12 hours
        if TimeUtils.judgeTimeDifference(registered['accurateTime']) >= 12:
            await userRegistration(userQQ, GoodMorningModel.NIGHT_MODEL.value)
            rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.NIGHT_MODEL.value)
            send += (await Utils.extractRandomWords(GoodMorningModel.NIGHT_MODEL.value, nickname) + '\n' +
                (await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.NIGHT_MODEL.value)).replace(r'{number}', str(rank)))
            return send
    if registered['model'] == GoodMorningModel.MORNING_MODEL.value:
        soberTime = TimeUtils.judgeTimeDifference(registered['accurateTime'])
        # too little time
        if soberTime <= 4:
            send += await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('unable_to_trigger', GoodMorningModel.NIGHT_MODEL.value)
            return send
        # sober time cannot exceed 24 hours
        await userRegistration(userQQ, GoodMorningModel.NIGHT_MODEL.value)
        if soberTime < 24:
            send += await Utils.extractRandomWords(GoodMorningModel.NIGHT_MODEL.value, nickname)
            rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.NIGHT_MODEL.value)
            send += ((await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.NIGHT_MODEL.value)).replace(r'{number}', str(rank)) + '\n')
            soberAccurateTime = TimeUtils.calculateTheElapsedTimeCombination(registered['accurateTime'])
            if soberAccurateTime[0] >= 12:
                send += TimeUtils.replaceHourMinuteAndSecond(soberAccurateTime, 
                            (await Utils.readConfiguration(GoodMorningModel.NIGHT_MODEL.value))['working_hours'][2]['content'])
            else:
                send += TimeUtils.replaceHourMinuteAndSecond(soberAccurateTime, 
                            random.choice((await Utils.readConfiguration(GoodMorningModel.NIGHT_MODEL.value))['working_hours'])['content'])
        else:
            rank = await addToCheckInPoolAndGetRanking(userQQ, userGroup, GoodMorningModel.NIGHT_MODEL.value)
            send += (await Utils.extractRandomWords(GoodMorningModel.NIGHT_MODEL.value, nickname) + '\n' +
                (await Utils.extractConfigurationInformationAccordingToSpecifiedParameters('suffix',
                GoodMorningModel.NIGHT_MODEL.value)).replace(r'{number}', str(rank)))
        return send
    return Status.FAILURE