# main.py
import re
import datetime
import requests

from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core.message import GroupMessage
from ncatbot.utils.logger import get_log

#from PIL import Image
#from PIL import ImageDraw
#from PIL import ImageFont

from pathlib import Path

# 获取日志记录器
_log = get_log()
_log.info("引用xibao")

NAME="traininfo"
VERSION = "1.0.0"
PLUGIN_ROOT = Path(__file__).parent

# 准备正则表达式
COMMAND_STYLE = re.compile(r"/(.*?)\s")
MSG_TEXT_STYLE = re.compile(r"\s([\s\S]*)")


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
    if traincode==False:
        return False
    else:
        date = today
        data_raw = requests.get('https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no={}&leftTicketDTO.train_date={}&rand_code='.format(traincode,date))
        data = data_raw.json()['data']['data']
        output_info = ''
        for i in data:
            output_info +=  '\n'+ i['station_name'] + "   " + i['arrive_time'] + "   " + i['start_time'] 
        return output_info

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
        message = get_journey(get_traincode(msg_text))
        if message == False:
            message = "未查询到相关信息，请检查车次是否正确~"
        else:
            message = "车次：{}\n".format(msg_text) + "途经站点   到点   开点 " + message
        

        await self.api.post_group_msg(msg.group_id, text=message)

    async def on_load(self):
        # 插件加载时执行的操作, 可缺省
        print(f"{self.name} 插件已加载")
        print(f"插件版本: {self.version}")
