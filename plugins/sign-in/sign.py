
from io import BytesIO

from .utils import Tools, Status, Network
from .config import highQuality
from .config import RESOURCES_BASE_PATH

from PIL import Image, ImageDraw, ImageFilter, ImageFont

class User():

    def __init__(self, nickname, favorability, days, hitokoto):
        self._userNickname = nickname
        self._userFavorability = favorability
        self._userSignInDays = days
        self._userHitokoto = hitokoto

        self._userInfo = '签 到 成 功'

        self._userInfoIntegration = f'签到天数  {self._userSignInDays}   好感度  {self._userFavorability}'


class SignIn(User):

    FONT_REEJI = 'REEJI-HonghuangLiGB-SemiBold.ttf'

    FONT_ZHANKU = 'zhanku.ttf'


    def __init__(self, userQQ, nickname, favorability, days, hitokoto, 
                        avatarUrl, basemapSize = 640, avatarSize = 256):

        super().__init__(nickname, favorability, days, hitokoto)

        self._userQQ = userQQ
        self._basemapSize = basemapSize
        self._avatarSize = avatarSize
        self._avatarUrl = avatarUrl

        self._img = Status.FAILURE
        self._roundImg = Status.FAILURE
        self._canvas = Status.FAILURE
        self._magicCircle = Status.FAILURE
        self._textBaseMap = Status.FAILURE

        self._magicCirclePlus = 30
        self._avatarVerticalOffset = 50
        self._textBaseMapSize = (540, 160)
        self._topPositionOfTextBaseMap = 425
        self._textBaseMapLeftPosition = int((self._basemapSize - self._textBaseMapSize[0]) / 2)
        self._fontAttenuation = 2
        self._minimumFontLimit = 10
        self._infoCoordinatesY = Tools.dictToObj({
            'nickname': self._topPositionOfTextBaseMap + 26,
            'info': self._topPositionOfTextBaseMap + 64,
            'integration': self._topPositionOfTextBaseMap + 102,
            'hitokoto': self._topPositionOfTextBaseMap + 137
        })
        self._infoFontSize = Tools.dictToObj({
            'nickname': 28,
            'info': 28,
            'integration': 25,
            'hitokoto': 25
        })
        self._infoFontName = Tools.dictToObj({
            'nickname': self.FONT_REEJI,
            'info': self.FONT_REEJI,
            'integration': self.FONT_REEJI,
            'hitokoto': self.FONT_ZHANKU
        })

    @staticmethod
    async def getPictures(url):
        img = await Network.getBytes(url)
        return img

    async def createAvatar(self):
        size = self._basemapSize
        avatarImgUrl = self._avatarUrl
        res = await self.getPictures(avatarImgUrl)
        self._img = self.resize(Image.open(BytesIO(res)).convert('RGBA'), (size, size))
        return self
        
    @staticmethod
    def resize(img, size):
        return img.copy().resize(size, Image.ANTIALIAS)

    @staticmethod
    def gaussianBlur(img, radius = 7):
        return img.copy().filter(ImageFilter.GaussianBlur(radius = radius))

    @staticmethod
    def imageRadiusProcessing(img, centralA, radius = 30):
        """处理图片四个圆角。
        :centralA: 中央区域的 A 通道值，当指定为 255 时全透，四角将使用 0 全不透
        """
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill = centralA)
        w, h = img.size
        alpha = Image.new('L', img.size, centralA)
        upperLeft, lowerLeft = circle.crop((0, 0, radius, radius)), circle.crop((0, radius, radius, radius * 2))
        upperRight, lowerRight = circle.crop((radius, 0, radius * 2, radius)), circle.crop((radius, radius, radius * 2, radius * 2))
        alpha.paste(upperLeft, (0, 0))
        alpha.paste(upperRight, (w - radius, 0))
        alpha.paste(lowerRight, (w - radius, h - radius))
        alpha.paste(lowerLeft, (0, h - radius))
        img.putalpha(alpha)
        return img

    def createRoundImg(self):
        img = self._img
        size = self._avatarSize

        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill = 255)

        self._roundImg = self.resize(img, (size, size))
        self._roundImg.putalpha(mask)
        return self


    def createCanvas(self):
        size = self._basemapSize
        self._canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        self._canvas.paste(self.gaussianBlur(self._img))
        return self
        

    def createAMagicCircle(self):
        size = self._magicCirclePlus + self._avatarSize
        magicCircle = Image.open(f'{RESOURCES_BASE_PATH}/magic-circle.png').convert('L')
        magicCircle = self.resize(magicCircle, (size, size))
        self._magicCircle = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        self._magicCircle.putalpha(magicCircle)
        return self

    def createTextBasemap(self, transparency = 190):
        self._textBaseMap = Image.new('RGBA', self._textBaseMapSize, (0, 0, 0, transparency))
        self._textBaseMap = self.imageRadiusProcessing(self._textBaseMap, transparency)
        return self

    def additionalMagicCircle(self):
        magicCircle = self._magicCircle
        x = int((self._basemapSize - self._avatarSize - self._magicCirclePlus) / 2)
        y = x - self._avatarVerticalOffset
        self._canvas.paste(magicCircle, (x, y), magicCircle)
        return self

    def additionalAvatar(self):
        avatar = self._roundImg
        x = int((self._basemapSize - self._avatarSize) / 2)
        y = x - self._avatarVerticalOffset
        self._canvas.paste(avatar, (x, y), avatar)
        return self

    def additionalTextBaseMap(self):
        textBaseMap = self._textBaseMap
        x = int((self._basemapSize - self._textBaseMapSize[0]) / 2)
        y = self._topPositionOfTextBaseMap
        self._canvas.paste(textBaseMap, (x, y), textBaseMap)
        return self

    def writePicture(self, img, text, position, fontName, fontSize, color = (255, 255, 255)):
        font = ImageFont.truetype(f'{RESOURCES_BASE_PATH}/font/{fontName}', fontSize)
        draw = ImageDraw.Draw(img)
        textSize = font.getsize(text)
        attenuation = self._fontAttenuation
        x = int(position[0] - textSize[0] / 2)
        limit = self._minimumFontLimit
        while x <= self._textBaseMapLeftPosition:
            fontSize -= attenuation
            if fontSize <= limit:
                return Status.FAILURE
            font = ImageFont.truetype(f'{RESOURCES_BASE_PATH}/font/{fontName}', fontSize)
            textSize = font.getsize(text)
            x = int(position[0] - textSize[0] / 2)
        y = int(position[1] - textSize[1] / 2)
        draw.text((x, y), text, color, font = font)
        return Status.SUCCESS


    def additionalSignInInformation(self):
        fontSize = self._infoFontSize
        coordinateY = self._infoCoordinatesY
        font = self._infoFontName
        x = int(self._basemapSize / 2)
        # Add user nickname
        result = self.writePicture(img = self._canvas, text = self._userNickname,
                                   position = (x, coordinateY.nickname), fontName = font.nickname, 
                                   fontSize = fontSize.nickname)
        if result == Status.FAILURE: return Status.FAILURE
        # Add success message
        result = self.writePicture(img = self._canvas, text = self._userInfo,
                                   position = (x, coordinateY.info), fontName = font.info, 
                                   fontSize = fontSize.info)
        if result == Status.FAILURE: return Status.FAILURE
        # Add integration information
        result = self.writePicture(img = self._canvas, text = self._userInfoIntegration,
                                   position = (x, coordinateY.integration), fontName = font.integration, 
                                   fontSize = fontSize.integration)
        if result == Status.FAILURE: return Status.FAILURE
        # Addition hitokoto
        result = self.writePicture(img = self._canvas, text = self._userHitokoto,
                                   position = (x, coordinateY.hitokoto), fontName = font.hitokoto, 
                                   fontSize = fontSize.hitokoto)
        if result == Status.FAILURE: return Status.FAILURE
        return self


    def save(self):
        dir = f'{RESOURCES_BASE_PATH}/cache'
        Tools.checkFolder(dir)
        if highQuality:
            path = f'{RESOURCES_BASE_PATH}/cache/{self._userQQ}.png'
            self._canvas.save(path)
        else:
            path = f'{RESOURCES_BASE_PATH}/cache/{self._userQQ}.jpg'
            self._canvas.convert('RGB').save(path)


    async def drawing(self):
        # Start generating
        result = await self.createAvatar()

        result = (result.createRoundImg()
                       .createCanvas()
                       .createAMagicCircle()
                       .createTextBasemap()
                       # Start processing
                       .additionalMagicCircle()
                       .additionalAvatar()
                       .additionalTextBaseMap()
                       # Must be the last step 
                       .additionalSignInInformation())
                       
        if result == Status.FAILURE: return result
        # Save
        result.save()
        return Status.SUCCESS