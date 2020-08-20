
import os
import random

from PIL import Image, ImageDraw, ImageFont

from .utils import Tools, Status, VtuberFortuneModel, TimeUtils

# 触发命令列表
commandList = ['今日人品', '今日运势', '抽签', '人品', '运势', '小狐狸签', '吹雪签']

RESOURCES_BASE_PATH = './plugins/vtuber-fortune/resource'


async def handlingMessages(msg, bot, userGroup, userQQ):
    match = Tools.commandMatch(msg, commandList)
    if match:
        # Determine if it has been used today
        if await testUse(userQQ) == Status.SUCCESS:
            model = VtuberFortuneModel.DEFAULT
            # Detect whether it is a small fox lottery
            if msg.find('小狐狸') != -1 or msg.find('吹雪') != -1:
                model = VtuberFortuneModel.LITTLE_FOX
            # Plot
            outPath = await drawing(model, userQQ)
            # Send a message
            await bot.send_image(
                cid = userGroup,
                file_path = outPath,
                at_user = userQQ
            )
            return


async def testUse(userQQ):
    Tools.checkFolder(RESOURCES_BASE_PATH)
    p = f'{RESOURCES_BASE_PATH}/user/{userQQ}.json'
    dir = f'{RESOURCES_BASE_PATH}/user'
    Tools.checkFolder(dir)
    content = await Tools.readJsonFile(p)
    if content == Status.FAILURE:
        userStructure = {
            'time': TimeUtils.getTheCurrentTime()
        }
        await Tools.writeJsonFile(p, userStructure)
        return Status.SUCCESS
    interval = TimeUtils.getTimeDifference(content['time'], TimeUtils.DAY)
    if interval >= 1:
        content['time'] = TimeUtils.getTheCurrentTime()
        await Tools.writeJsonFile(p, content)
        return Status.SUCCESS
    return Status.FAILURE


def randomBasemap():
    p = f'{RESOURCES_BASE_PATH}/img'
    return p + '/' + random.choice(os.listdir(p))


async def copywriting():
    p = f'{RESOURCES_BASE_PATH}/fortune/copywriting.json'
    content = await Tools.readJsonFile(p)
    return random.choice(content['copywriting'])


async def getTitle(structure):
    p = f'{RESOURCES_BASE_PATH}/fortune/goodLuck.json'
    content = await Tools.readJsonFile(p)
    for i in content['types_of']:
        if i['good-luck'] == structure['good-luck']:
            return i['name']
    raise Exception('Configuration file error')


def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = ' '
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [numberOfSlices, text[:int(length / 2)] + fillIn, fillIn + text[int(length / 2):]]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [numberOfSlices, text[:int((length + 1) / 2)] + fillIn,
                                    fillIn + space + text[int((length + 1) / 2):]]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality:(i + 1) * cardinality])
    return result


def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return '\n'.join(list)


def exportFilePath(originalFilePath, userQQ):
    outPath = originalFilePath.replace('/img/', '/out/').replace('frame', str(userQQ))
    dirPath = f'{RESOURCES_BASE_PATH}/out'
    Tools.checkFolder(dirPath)
    return outPath


async def drawing(model, userQQ):
    fontPath = {
        'title': f'{RESOURCES_BASE_PATH}/font/Mamelon.otf',
        'text': f'{RESOURCES_BASE_PATH}/font/sakura.ttf'
    }
    imgPath = randomBasemap()
    if model == VtuberFortuneModel.LITTLE_FOX:
        imgPath = f'{RESOURCES_BASE_PATH}/img/frame_17.png'
    img = Image.open(imgPath)
    # Draw title
    draw = ImageDraw.Draw(img)
    text = await copywriting()
    title = await getTitle(text)
    text = text['content']
    font_size = 45
    color = '#F5F5F5'
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath['title'], font_size)
    font_length = ttfront.getsize(title)
    draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
                title, fill=color,font=ttfront)
    # Text rendering
    font_size = 25
    color = '#323232'
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath['text'], font_size)
    result = decrement(text)
    if not result[0]:
        return 
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(image_font_center[0] + (result[0] - 2) * font_size / 2 + 
                (result[0] - 1) * 4 - i * (font_size + 4))
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill = color, font = ttfront)
    # Save
    outPath = exportFilePath(imgPath, userQQ)
    img.save(outPath)
    return outPath