
import random
from io import BytesIO

from .utils import Network, Tools
from .config import creep_limit, RESOURCES_BASE_PATH

from PIL import Image, ImageDraw


class ThrowAndCreep():

    _avatar_size = 139

    _center_pos = (17, 180)

    @staticmethod
    async def getAvatar(url):
        img = await Network.getBytes(url)
        return img

    @staticmethod
    def randomClimb():
        randomNumber = random.randint(1, 100)
        if randomNumber < creep_limit:
            return True
        return False

    @staticmethod
    def get_circle_avatar(avatar, size):
        avatar.thumbnail((size, size))

        scale = 5
        mask = Image.new('L', (size*scale, size*scale), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size * scale, size * scale), fill=255)
        mask = mask.resize((size, size), Image.ANTIALIAS)

        ret_img = avatar.copy()
        ret_img.putalpha(mask)

        return ret_img

    @classmethod
    async def creep(cls, qq, avatar_img_url):
        creeped_who = qq
        id = random.randint(0, 53)

        whetherToClimb = cls.randomClimb()

        if not whetherToClimb:
            return f'{RESOURCES_BASE_PATH}/不爬.jpg'

        res = await cls.getAvatar(avatar_img_url)
        avatar = Image.open(BytesIO(res)).convert('RGBA').resize((640, 640), Image.ANTIALIAS)
        avatar = cls.get_circle_avatar(avatar, 100)

        creep_img = Image.open(f'{RESOURCES_BASE_PATH}/pa/爬{id}.jpg').convert('RGBA')
        creep_img = creep_img.resize((500, 500), Image.ANTIALIAS)
        creep_img.paste(avatar, (0, 400, 100, 500), avatar)
        dirPath = f'{RESOURCES_BASE_PATH}/avatar'
        Tools.checkFolder(dirPath)
        creep_img.save(f'{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png')

        return f'{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png'

    @classmethod
    async def throw(cls, qq, avatar_img_url):
        throwed_who = qq

        res = await cls.getAvatar(avatar_img_url)
        avatar = Image.open(BytesIO(res)).convert('RGBA').resize((640, 640), Image.ANTIALIAS)
        avatar = cls.get_circle_avatar(avatar, cls._avatar_size)

        rotate_angel = random.randrange(0, 360)

        throw_img = Image.open(f'{RESOURCES_BASE_PATH}/throw.jpg').convert('RGBA')
        throw_img.paste(avatar.rotate(rotate_angel), cls._center_pos, avatar.rotate(rotate_angel))
        dirPath = f'{RESOURCES_BASE_PATH}/avatar'
        Tools.checkFolder(dirPath)
        throw_img.save(f'{RESOURCES_BASE_PATH}/avatar/{throwed_who}.png')

        return f'{RESOURCES_BASE_PATH}/avatar/{throwed_who}.png'