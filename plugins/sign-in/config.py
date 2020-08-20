
RESOURCES_BASE_PATH = './plugins/sign-in/resource'

# 触发命令列表
commandList = ['签到']
# 是否开启高质量图片，默认是，请根据网络情况选择：
#  - 高质量图片单张在 400 KB 左右，采用 PNG 格式，色彩鲜艳。
#  - 若不开启，请置为 False ，单张在 100 KB 以内，采用 JPG 格式，少许模糊并丢失 A 通道部分效果。
highQuality = True
# 是否打开一言，若不打开，默认显示 noHitokoto
hitokotoOpen = True
# 当获取一言失败且调取本地历史一言存档也失败时，展示的话
noHitokoto = '今天也要元气满满哦~'
# 一言黑名单，含有该内容即重新获取
hitokotoBlacklist = ['历史的发展', '没有调查']
# 一言存档开关，当网络错误或一言网站倒闭时，采用本地存档
hitokotoArchiveOpen = True