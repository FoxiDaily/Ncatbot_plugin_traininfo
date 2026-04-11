# Ncatbot5 TrainInfoPlugin - 火车信息查询插件

这是一个适用于 Ncatbot5 框架的火车信息查询插件，可以实时查询中国铁路车次信息和行程详情。

## 📁 项目结构

```
ncatbot5_plugin_traininfo/
└── TrainInfoPlugin/          # 插件主目录
    ├── __init__.py           # 插件声明文件
    ├── main.py               # 主插件代码
    ├── requirements.txt      # Python 依赖
    ├── README.md             # 插件使用说明
    └── output/               # 输出目录（运行时自动创建）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests>=2.31.0
```

### 2. 部署插件

将 `TrainInfoPlugin` 文件夹复制到你的 Ncatbot5 项目的 `plugins/` 目录下：

```
your-ncatbot-project/
├── plugins/
│   └── TrainInfoPlugin/    <-- 复制到这里
├── config.yaml
└── ...
```

### 3. 启动 Bot

```bash
ncatbot run
```

### 4. 使用插件

在 QQ 群聊或私聊中发送：

```
/train G1234
```

## 📖 详细文档

查看 [TrainInfoPlugin/README.md](TrainInfoPlugin/README.md) 获取完整的使用说明和配置指南。

## ✨ 功能特性

- ✅ 实时查询 12306 车次信息
- ✅ 支持所有类型的列车（G/D/C/Z/T/K 等）
- ✅ 显示完整的行程和站点信息
- ✅ 支持群聊和私聊
- ✅ 友好的文本格式输出
- ✅ 完善的错误处理和日志记录

## 🔧 技术栈

- **框架**: Ncatbot5
- **语言**: Python 3.12+
- **数据源**: 12306 API
- **依赖**: requests

## 📝 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `/train <车次>` | 查询车次信息 | `/train G1234` |
| `/train about` | 查看插件信息 | `/train about` |

## ⚠️ 注意事项

1. 本插件需要网络连接才能正常工作
2. 车次信息以 12306 官方数据为准
3. 仅支持查询当天的车次信息
4. 请遵守 12306 API 使用规范，避免频繁请求

## 📄 许可证

本项目基于 MIT 协议开源。

## 🙏 致谢

- [Ncatbot5](https://github.com/ncatbot/NcatBot) - QQ 机器人框架
- [12306](https://www.12306.cn/) - 车次数据源
- [FoxiDaily/Ncatbot_plugin_traininfo](https://github.com/FoxiDaily/Ncatbot_plugin_traininfo) - 参考实现

## 📮 反馈

如有问题或建议，欢迎提交 Issue。

---

**祝您旅途愉快！🚄**
