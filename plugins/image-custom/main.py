
import os

from .utils import Tools, Model, Status
from .config import RESOURCES_BASE_PATH, qrListOpen, fontPath

from PIL import ImageDraw, Image, ImageFont

if qrListOpen:
    import qrcode


async def mainEntrance(msg, userQQ, userGroup, bot):
    pictureListCommand = ['img list']
    primaryMatchingSuffix = ['.jpg', '.JPG']
    switchEmojiCommandPrefix = ['img ']
    # Emoticon list function
    if Tools.commandMatch(msg, pictureListCommand, Model.ALL):
        await makeQrCode()
        listFilePath = f"{RESOURCES_BASE_PATH}/list.jpg"
        if os.path.exists(listFilePath):
            
            await bot.send_image(
                cid = userGroup,
                file_path = listFilePath
            )

            return
    # Render emoji function
    if Tools.commandMatch(msg, primaryMatchingSuffix, Model.BLURRY):
        text = msg[:msg.rfind('.')]
        emoticonId = await getEmojiId(userQQ)
        result = await drawing(emoticonId, text, userQQ)
        if result == Status.SUCCESS:
            resultPath = f'{RESOURCES_BASE_PATH}/cache/{userQQ}.jpg'

            await bot.send_image(
                cid = userGroup,
                file_path = resultPath
            )

            return
    # Change emoji function
    if Tools.commandMatch(msg, switchEmojiCommandPrefix, Model.BLURRY):
        emoticonAlias = msg[msg.find(' ') + 1:]
        result = await changeEmoji(userQQ, emoticonAlias)
        if result == Status.SUCCESS:
            sendMsg = f'表情已更换为 [{emoticonAlias}] 喵~'

            await bot.send_text(
                cid = userGroup,
                content = f'<@{userQQ}>  {sendMsg}'
            )

            return


async def makeQrCode():
    if qrListOpen:
        p = f'{RESOURCES_BASE_PATH}/image_data/bieming/name.ini'
        lines = await Tools.readFileByLine(p)
        if lines == Status.FAILURE:
            raise Exception(f'{p} 表情包配置不存在！')
        out = ''
        for line in lines:
            name = line.strip().split()[0]
            out += name + '\n'
        out = out.strip()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=5,
            border=4,
        )
        qr.add_data(out)
        img = qr.make_image(fill_color="green", back_color="white")
        img.save(f'{RESOURCES_BASE_PATH}/list.jpg')


async def getEmojiId(userQQ):
    p = f'{RESOURCES_BASE_PATH}/image_data/qqdata/{userQQ}.ini'
    c = await Tools.readFileContent(p)
    return 'initial' if c == Status.FAILURE else c


async def drawing(emoticonId, text, userQQ):
    picPathJPG = f'{RESOURCES_BASE_PATH}/image_data/{emoticonId}/{emoticonId}.jpg'
    picPathPNG = f'{RESOURCES_BASE_PATH}/image_data/{emoticonId}/{emoticonId}.png'
    picPath = ''
    # Check that the file exists
    if os.path.exists(picPathJPG):
        picPath = picPathJPG
    elif os.path.exists(picPathPNG):
        picPath = picPathPNG
    else:
        return Status.FAILURE
    configPath = f'{RESOURCES_BASE_PATH}/image_data/{emoticonId}/config.ini'
    if not os.path.exists(configPath):
        return Status.FAILURE

    # Drawing
    config = await Tools.readJsonFile(configPath)
    img = Image.open(picPath)
    draw = ImageDraw.Draw(img)
    color = config['color']
    fontSize = config['font_size']
    fontMax = config['font_max']
    imageFontCenter = (config["font_center_x"], config["font_center_y"])
    imageFontSub = config["font_sub"]
    # 设置字体暨字号
    ttfront = ImageFont.truetype(fontPath,fontSize) 
    fontLength = ttfront.getsize(text)
    while fontLength[0]>fontMax:
        fontSize -= imageFontSub
        ttfront = ImageFont.truetype(fontPath, fontSize)
        fontLength = ttfront.getsize(text)
    if fontSize <= 15:
        return Status.FAILURE
    # 自定义打印的文字和文字的位置
    if fontLength[0] > 5:
        draw.text((imageFontCenter[0] - fontLength[0]/2, imageFontCenter[1] - fontLength[1]/2),
                    text, fill = color, font = ttfront)

    dirPath = f'{RESOURCES_BASE_PATH}/cache'
    Tools.checkFolder(dirPath)
    img.save(f'{dirPath}/{userQQ}.jpg')
    return Status.SUCCESS


async def changeEmoji(userQQ, emoticonAlias):
    emojiConfiguration = f'{RESOURCES_BASE_PATH}/image_data/bieming/name.ini'
    if not os.path.exists(emojiConfiguration):
        raise Exception(f'表情配置 {emojiConfiguration} 不存在！')
    emoticonId = await queryEmoticonId(emoticonAlias)
    currentEmoji = await getEmojiId(userQQ)
    if emoticonId != Status.FAILURE and emoticonId != currentEmoji:
        p = f'{RESOURCES_BASE_PATH}/image_data/qqdata/{userQQ}.ini'
        await Tools.writeFile(p, emoticonId)
        return Status.SUCCESS
    return Status.FAILURE


async def queryEmoticonId(emoticonAlias):
    emojiConfiguration = f'{RESOURCES_BASE_PATH}/image_data/bieming/name.ini'
    if not os.path.exists(emojiConfiguration):
        raise Exception(f'表情配置 {emojiConfiguration} 不存在！')
    for line in await Tools.readFileByLine(emojiConfiguration):
        line = line.strip()
        alias = line.split(' ')[0]
        codename = line.split(' ')[1]
        if alias == emoticonAlias:
            return codename
    return Status.FAILURE