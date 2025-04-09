# main.py
import re
import os
import datetime
import requests

from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core.message import GroupMessage
from ncatbot.utils.logger import get_log

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


from pathlib import Path

# 获取日志记录器
_log = get_log()


NAME="traininfo"
VERSION = "1.1.0"
PLUGIN_ROOT = Path(__file__).parent

# 准备正则表达式
COMMAND_STYLE = re.compile(r"/(.*?)\s")
MSG_TEXT_STYLE = re.compile(r"\s([\s\S]*)")

# 创建不存在的output文件夹
if not os.path.exists(PLUGIN_ROOT/"output"):
    os.mkdir(PLUGIN_ROOT/"output")


bot = CompatibleEnrollment  # 兼容回调函数注册器
today = datetime.date.today()

# 获取车次编号
def get_traincode(train_no):
    date=today.strftime("%Y%m%d")
    data_raw = requests.get("https://search.12306.cn/search/v1/train/search?keyword={}&date={}".format(train_no,date))
    data=data_raw.json()['data']
    for i in data:
        if i["station_train_code"]==train_no:
            return i["train_no"]        
    else:
        print('No trains.')
        return False

# 获取行程信息
def get_journey(traincode):
    station = ""
    arrive = ""
    leave = ""
    row = 0
    if traincode==False:
        return False
    else:
        date = today
        data_raw = requests.get('https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no={}&leftTicketDTO.train_date={}&rand_code='.format(traincode,date))
        data = data_raw.json()['data']['data']
        for i in data:
            station += i['station_name'] + "\n"
            arrive += i['arrive_time'] + "\n"
            leave += i['start_time'] + "\n"
            row += 1
        return (station,arrive,leave,row)

class traininfo(BasePlugin):
    name = NAME # 插件名称
    version = VERSION  # 插件版本

    @bot.group_event()
    async def on_group_event(self, msg: GroupMessage):
        # 在文本最后加入一个空白字符，防止输入单命令如“/xxx”导致的正则表达式匹配失败
        raw_message = msg.raw_message+" "
        if raw_message[0] != "/":
            return None
        command = COMMAND_STYLE.search(raw_message).group(1)
        msg_text = MSG_TEXT_STYLE.search(raw_message).group(1).strip()
        # 检查命令是否有效
        if command not in ("train"):
            return None
        # 如果输入字符太多就拒绝处理
        if len(msg_text) > 7:
            await self.api.post_group_msg(msg.group_id, text="这还是国铁的车吗？检查一下车次信息叭~")
            return None
        
        # 开始获取信息
        print("Getting train info of {}".format(msg_text))
        result = get_journey(get_traincode(msg_text.upper()))

        if result == False:
            message = "未查询到相关信息，请检查车次是否正确~"
            await self.api.post_group_msg(msg.group_id, text=message)
        else:
            station,arrive,leave,row=result

            # 开始绘制图片
            img = Image.new('RGBA', (1080,  600 + 72*row), 'white')
            status_bar = Image.open(PLUGIN_ROOT/"resources/status_bar.png")
            background = Image.open(PLUGIN_ROOT/"resources/bg.png")

            idraw = ImageDraw.Draw(img)
            if img.height<=1500:  # 绘制背景国铁logo
                img.paste(background.resize((300,300)), (390,  36*row+280))
            else:
                img.paste(background, (240,  36*row+50))
            img.paste(status_bar, (0, 0))   # 绘制标题栏

            # 绘制车次和日期
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=40)
            idraw.text((15, 10), "车次：" + msg_text.upper(), font=font,fill=(255, 255, 255))
            idraw.text((850, 10),  str(today), font=font,fill=(255, 255, 255))

            # 绘制小标题
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=40)
            for x in (60,62):
                for y in (320,322):
                    idraw.text((x, y), "途经车站", font=font,fill=(0, 105, 82))
                    idraw.text((x+540, y), "到点", font=font,fill=(0, 105, 82))
                    idraw.text((x+790, y), "开点", font=font,fill=(0, 105, 82))
            
            # 绘制正文
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=60)
            idraw.text((60, 400), station, font=font,fill=(0, 0, 0))
            idraw.text((600, 400), arrive, font=font,fill=(0, 0, 0))
            idraw.text((850, 400), leave, font=font,fill=(0, 0, 0))
            img.save(PLUGIN_ROOT/"output/train.png")

            await self.api.post_group_msg(msg.group_id, image=str(PLUGIN_ROOT/"output/train.png"))

    async def on_load(self):
        # 插件加载时执行的操作, 可缺省
        print(f"{self.name} 插件已加载")
        print(f"插件版本: {self.version}")
