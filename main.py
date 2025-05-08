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


NAME = "traininfo"
VERSION = "2.0.0"
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
    today = datetime.date.today()
    date = today.strftime("%Y%m%d")
    data_raw = requests.get("https://search.12306.cn/search/v1/train/search?keyword={}&date={}".format(train_no,date))
    data = data_raw.json()['data']
    for i in data:
        if i["station_train_code"] == train_no:
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
    if traincode == False:
        return False
    else:
        today = datetime.date.today()
        date = today
        data_raw = requests.get('https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no={}&leftTicketDTO.train_date={}&rand_code='.format(traincode,date))
        # data_raw_2 = requests.get('https://mobile.12306.cn/weixin/wxcore/queryByTrainNo?train_no={}&depart_date={}'.format(traincode,date))
        data = data_raw.json()['data']['data']
        for i in data:
            station += i['station_name'] + "\n"
            arrive += i['arrive_time'] + "\n"
            leave += i['start_time'] + "\n"
            row += 1
        start = data[0]['station_name']
        end = data[-1]['station_name']
        time = data[-1]["running_time"]
        return (station,arrive,leave,row,start,end,time)

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
            station,arrive,leave,row,start,end,time=result
            running_time = time.split(":")
            
            # 初始化画布
            img = Image.new('RGBA', (1080,  800 + 72*row), (230,230,230))

            # 加载图片资源
            # 判断车型
            if msg_text.upper()[0] == "G":
                color = (198,40,40)
                train_type = "gaosu"
                status_bar = Image.open(PLUGIN_ROOT/"resources/red.png")

            elif msg_text.upper()[0] == "D":
                color = (21,101,192)
                train_type = "dongche"
                status_bar = Image.open(PLUGIN_ROOT/"resources/blue.png")

            elif msg_text.upper()[0] == "C":
                color = (21,101,192)
                train_type = "chengji"
                status_bar = Image.open(PLUGIN_ROOT/"resources/blue.png")

            else:
                color = (46,125,50)
                train_type = "pusu"
                status_bar = Image.open(PLUGIN_ROOT/"resources/green.png")

            
            #background = Image.open(PLUGIN_ROOT/"resources/bg.png")
           
            # 绘制标题栏
            idraw = ImageDraw.Draw(img)
            img.paste(status_bar, (0, 0))   

            # 绘制车次和日期
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/SWISSCK.TTF" , size=90)
            idraw.text((90, 315), msg_text.upper()[0] , font = font , fill = color)
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/SWISSCK.TTF" , size=60)
            idraw.text((145, 344) , msg_text.upper()[1:] , font = font , fill = (0,0,0))
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=50)
            idraw.text((540, 20) , str(today) , anchor="ma" , font = font , fill = (255,255,255))

            # 绘制车型
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=30)
            if train_type == "gaosu":
                idraw.text((907, 343) , "高速" , font = font , fill = (255,255,255))
            elif train_type == "dongche":
                idraw.text((907, 343) , "动车" , font = font , fill = (255,255,255))
            elif train_type == "chengji":
                idraw.text((907, 343) , "城际" , font = font , fill = (255,255,255))
            else:
                idraw.text((907, 343) , "普速" , font = font , fill = (255,255,255))

            # 绘制始末站
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=35)
            idraw.text((80, 457) , start + " → " + end + " | " + "{}时{}分".format(running_time[0] , running_time[1]) , font = font , fill = (255,255,255))


            # 绘制小标题
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=40)
            for x in (60,62):
                for y in (570,572):
                    idraw.text((x, y) , "途经车站" , font = font , fill = color)
                    idraw.text((x+540, y) , "到点" ,  font = font , fill = color)
                    idraw.text((x+790, y) , "开点" ,  font = font , fill = color)
            
            # 绘制正文
            font = ImageFont.truetype(font=PLUGIN_ROOT/"resources/siyuan.otf" , size=60)
            idraw.text((60, 650) , station , font = font , fill = (0, 0, 0))
            idraw.text((600, 650) , arrive , font = font , fill = (0, 0, 0))
            idraw.text((850, 650) , leave , font = font , fill = (0, 0, 0))
            img.save(PLUGIN_ROOT/"output/train.png")

            await self.api.post_group_msg(msg.group_id , image = str(PLUGIN_ROOT/"output/train.png"))

    async def on_load(self):
        # 插件加载时执行的操作, 可缺省
        print(f"{self.name} 插件已加载")
        print(f"插件版本: {self.version}")
