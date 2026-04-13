# main.py
import re
import os
import datetime
import requests

from ncatbot.plugin import BasePlugin
from ncatbot.core import registrar
from ncatbot.event.qq import GroupMessageEvent
from ncatbot.utils.logger import get_log

from PIL import Image as PILImage
from PIL import ImageDraw
from PIL import ImageFont


from pathlib import Path

_log = get_log()


NAME = "traininfo"
VERSION = "5.0.2"
PLUGIN_ROOT = Path(__file__).parent

# 准备正则表达式
COMMAND_STYLE = re.compile(r"/(.*?)\s")
MSG_TEXT_STYLE = re.compile(r"\s([\s\S]*)")

# 创建不存在的output文件夹
if not os.path.exists(PLUGIN_ROOT/"output"):
    os.mkdir(PLUGIN_ROOT/"output")


# 获取车次编号
def get_traincode(train_no):
    today = datetime.date.today()
    date = today.strftime("%Y%m%d")
    data_raw = requests.get("https://search.12306.cn/search/v1/train/search?keyword={}&date={}".format(train_no,date))
    data = data_raw.json()['data']
    for i in data:
        if i["station_train_code"] == train_no:
            return i["train_no"]        
    else:
        _log.warning('No trains.')
        return False

#获取车型信息
def get_traintype(train):
    data_raw = requests.get("https://api.rail.re/train/{}".format(train))
    _log.debug(f"Train type API response: {data_raw}")
    if str(data_raw) == "<Response [404]>":
        return ""
    else:
        data = data_raw.json()   
        traintype = data[0]["emu_no"][:-4]
        _log.info(f"车型: {traintype}")
        return traintype

# 获取行程信息
def get_journey(traincode):
    station = []
    arrive = []
    leave = []
    row = 0
    if traincode == False:
        return False
    else:
        today = datetime.date.today()
        date = today
        data_raw = requests.get('https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no={}&leftTicketDTO.train_date={}&rand_code='.format(traincode,date))
        data = data_raw.json()['data']['data']
        for i in data:
            station.append(i['station_name'])
            arrive.append(i['arrive_time'])
            leave.append(i['start_time'])
            row += 1
        start = data[0]['station_name']
        end = data[-1]['station_name']
        time = data[-1]["running_time"]
        return (station,arrive,leave,row,start,end,time)

class traininfo(BasePlugin):
    name = NAME  # 插件名称（需与 manifest.toml 一致）
    version = VERSION  # 插件版本（需与 manifest.toml 一致）

    @registrar.qq.on_group_message()
    async def on_group_event(self, event: GroupMessageEvent):
        # 在文本最后加入一个空白字符，防止输入单命令如"/xxx"导致的正则表达式匹配失败
        _log.debug("Received message: " + event.raw_message)
        raw_message = event.raw_message + " "
        if raw_message[0] != "/":
            return None
        command = COMMAND_STYLE.search(raw_message).group(1)
        msg_text = MSG_TEXT_STYLE.search(raw_message).group(1).strip()
        # 检查命令是否有效
        if command != "train":
            return None
        # 如果输入字符太多就拒绝处理
        if len(msg_text) > 7:
            reply = "这还是国铁的车吗？检查一下车次信息叭~"
            await event.reply(reply)
            _log.info("回复：" + reply)
            return None
        if msg_text == "about":
            reply = "\n感谢使用train_info插件！这是一个用来获取实时铁路车次信息的群机器人插件。\n本插件基于NcatBot引擎，使用Python编写，基于MIT协议开源，禁止用于商业用途。\n如果你有任何关于插件的建议或意见，或者你认为本插件侵犯了你的合法权益，欢迎在Git仓库提交issue！\n\n开源代码：https://git.szzy.tech:14514/FXDaily/Ncatbot_plugin_traininfo\n开发者：FXDaily\n列车素材：Bilibili@HXD1D0390\n车型数据源：rail.re\n车次信息数据源：12306.cn\n\n插件版本：{}".format(VERSION)
            await event.reply(reply)
            _log.info("回复：" + reply)
            return None
        # 开始获取信息
        _log.info(f"Getting train info of {msg_text}")
        result = get_journey(get_traincode(msg_text.upper()))

        if result is False:
            message = "未查询到相关信息，请检查车次是否正确~"
            await event.reply(message)
        else:
            station, arrive, leave, row, start, end, time = result
            traintype = get_traintype(msg_text.upper())
            running_time = time.split(":")
            
            # 初始化画布
            img = PILImage.new('RGBA', (1080, 800 + 100 * row), (230, 230, 230))

            # 加载图片资源
            # 判断车型
            if msg_text.upper()[0] == "G":
                color = (198, 40, 40)
                train_type = "gaosu"
                status_bar = PILImage.open(PLUGIN_ROOT / "resources/red.png")
            elif msg_text.upper()[0] == "D":
                color = (21, 101, 192)
                train_type = "dongche"
                status_bar = PILImage.open(PLUGIN_ROOT / "resources/blue.png")
            elif msg_text.upper()[0] == "C":
                color = (21, 101, 192)
                train_type = "chengji"
                status_bar = PILImage.open(PLUGIN_ROOT / "resources/blue.png")
            else:
                color = (46, 125, 50)
                train_type = "pusu"
                status_bar = PILImage.open(PLUGIN_ROOT / "resources/green.png")

            if traintype == "CR200J":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr200j.png")
            elif traintype == "CR200JC":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr200jc.png")
            elif traintype == "CRH2A" or traintype == "CRH2B" or traintype == "CRH2E":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh2abe.png")
            elif traintype == "CRH2C":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh2c.png")
            elif traintype == "CRH3C":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh3c.png")
            elif traintype == "CRH380A" or traintype == "CRH380AL" or traintype == "CRH380AN":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh380aln.png")
            elif traintype == "CRH380B" or traintype == "CRH380BL" or traintype == "CRH380BG" :
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh380bl.png")
            elif traintype == "CRH380CL":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh380cl.png")
            elif traintype == "CRH380D":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/crh380d.png")
            elif traintype == "CR400AFZ" or traintype == "CR400AFBS" or traintype == "CR400AFBZ" or traintype == "CR400AFS" or traintype == "CR400AFC":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr400afz.png")
            elif traintype == "CR400BFZ" or traintype == "CR400BFGZ" or traintype == "CR400BFBS" or traintype == "CR400BFBZ" or traintype == "CR400BFAZ" or traintype == "CR400BFS":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr400bfz.png")
            elif traintype=="CR300AF":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr300af.png")
            elif traintype=="CR300BF":
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr300bf.png")
            elif traintype == "CR400AF" or traintype == "CR400AFG" or traintype == "CR400AFB" or traintype == "CR400AFA" :
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr400af.png")
            elif traintype == "CR400BF" or traintype == "CR400BFB" or traintype == "CR400BFA" or traintype == "CR400BFG" :
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/cr400bf.png")
            else:
                train_img = PILImage.open(PLUGIN_ROOT / "resources/train/default.png")

            # background = Image.open(PLUGIN_ROOT/"resources/bg.png")

            # 绘制标题栏
            idraw = ImageDraw.Draw(img)
            img.paste(status_bar, (0, 0))

            # 绘制车次和日期
            today = datetime.date.today()
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/SWISSCK.TTF", size=90)
            idraw.text((90, 315), msg_text.upper()[0], font=font, fill=color)
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/SWISSCK.TTF", size=60)
            idraw.text((145, 344), msg_text.upper()[1:], font=font, fill=(0, 0, 0))
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/SWISSCK.TTF", size=50)
            idraw.text((540, 30), str(today), anchor="ma", font=font, fill=(255, 255, 255))

            # 绘制车型
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/siyuan.otf", size=30)
            if train_type == "gaosu":
                idraw.text((907, 343), "高速", font=font, fill=(255, 255, 255))
            elif train_type == "dongche":
                idraw.text((907, 343), "动车", font=font, fill=(255, 255, 255))
            elif train_type == "chengji":
                idraw.text((907, 343), "城际", font=font, fill=(255, 255, 255))
            else:
                idraw.text((907, 343), "普速", font=font, fill=(255, 255, 255))
            img.paste(train_img, (0, 800+100 * row-150))

            # 绘制始末站和型号
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/siyuan.otf", size=35)
            idraw.text((80, 457), start + " → " + end + " | " + "{}时{}分".format(running_time[0], running_time[1]), font=font, fill=(255, 255, 255))
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/SWISSCK.TTF", size=40)
            idraw.text((990, 461), traintype, anchor="ra", font=font, fill=(255, 255, 255))

            # 绘制站点
            for i in range(row):
                stop = PILImage.open(PLUGIN_ROOT / "resources/stop.png")
                img.paste(stop, (50, 640 + 100 * i))

            # 绘制小标题
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/siyuan.otf", size=40)
            for x in (60, 62):
                for y in (570, 572):
                    idraw.text((x, y), "途经车站", font=font, fill=color)
                    idraw.text((x + 540, y), "到点", font=font, fill=color)
                    idraw.text((x + 790, y), "开点", font=font, fill=color)

            # 绘制正文
            font = ImageFont.truetype(font=PLUGIN_ROOT / "resources/siyuan.otf", size=50)

            for i in range(row):
                idraw.text((120, 650 + 100 * i), station[i], font=font, fill=(0, 0, 0))
                idraw.text((600, 650 + 100 * i), arrive[i], font=font, fill=(0, 0, 0))
                idraw.text((850, 650 + 100 * i), leave[i], font=font, fill=(0, 0, 0))

            img.save(PLUGIN_ROOT / "output/train.png")

            # 使用 event.reply() 自动引用原消息
            await event.reply(image=str(PLUGIN_ROOT / "output/train.png"))

    async def on_load(self):
        """插件加载时执行的操作"""
        _log.info(f"{self.name} 插件已加载")
        _log.info(f"插件版本: {self.version}")
