# main.py
from pathlib import Path

from ncatbot.core.message import GroupMessage
from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.utils.logger import get_log

# 获取日志记录器
_log = get_log()
_log.info("引用Template")


# 插件名称
NAME = "Template"
# 插件版本号
VERSION = "1.0.0"
# 在用到路径时使用 PLUGIN_ROOT/"path"
PLUGIN_ROOT = Path(__file__).parent


bot = CompatibleEnrollment  # 兼容回调函数注册器


class Template(BasePlugin):
    name = NAME
    version = VERSION

    @bot.group_event()
    async def on_group_event(self, msg: GroupMessage):
        pass
        # 在这里写上读指令的方法
        if 1+1 == 3:
            pass
            # 在这里实现功能
            await self.api.post_group_msg(msg.group_id, text="模板")

    async def on_load(self):
        # 插件加载时执行的操作, 可缺省
        print(f"{self.name} 插件已加载")
        print(f"插件版本: {self.version}")


if __name__ == "__main__":
    # 在这里进行测试
    pass
