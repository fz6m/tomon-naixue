<div align="center">


<img src = 'https://cdn.jsdelivr.net/gh/fz6m/Private-picgo@moe/img/20200821032755.png' width = '150px' />

# naixue-bot

![Python](https://img.shields.io/badge/python-3.7%20%2B-informational)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Version](https://img.shields.io/badge/aiotomon-1.4-orange)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![License](https://img.shields.io/github/license/fz6m/tomon-naixue)

</div>

## 使用
### 安装依赖

#### SDK
```bash
    # 安装
    pip install git+https://github.com/fz6m/aiotomon.git@master

    # 升级
    pip install --upgrade git+https://github.com/fz6m/aiotomon.git@master
```

#### 必备依赖

你可以使用批量安装：
```bash
    pip install -r requirements.txt
```

或者手动安装：
```bash
    pip install pillow
    pip install qrcode
    pip install python-dateutil
    pip install aiohttp
    pip install aiofiles
```

#### 可选依赖
```bash
    pip install ujson
```
注：使用 `ujson` 可加速对 `.json` 文件的处理速度。


### 配置令牌

在 `config.py` 内填写你的 bot token 令牌

### 部署启动

```bash
    python bot.py
```

## 插件功能
 * 自定义表情包
 * 关注早晚安
 * Vtuber 运势
 * 可以爬了吗
 * Strings 签到

## 常见问题

#### 无法下载 SDK
本机需要安装 git 。

#### 安装 SDK 失败
升级你的 `setuptools` ：
```bash
    pip install --upgrade --ignore-installed setuptools
```

#### 依赖下载慢
使用大清镜像源，例：
```bash
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple python-dateutil
```

#### ujson 安装失败
如果安装 `ujson` 依赖失败，你可以放弃安装，从而会自动使用已有 `json` 库代替 `ujson` （性能较低），你也可以在 [这里](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ujson) 下载对应你 `python` 版本和位数的 `ujson` 安装包，之后执行本地安装即可：
```bash
    pip install 本地 ujson 安装包(.whl)路径
```

## 其他

#### 异步高性能 SDK
项目地址：[fz6m / aiotomon](https://github.com/fz6m/aiotomon)

#### 插件其他版本
[opqqq-plugin](https://github.com/fz6m/opqqq-plugin)

~~[nonebot-plugin](https://github.com/fz6m/nonebot-plugin)~~（EOF）
