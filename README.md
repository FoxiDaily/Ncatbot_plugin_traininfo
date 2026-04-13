# Ncatbot5 TrainInfoPlugin - 火车信息查询插件

这是一个适用于 Ncatbot5 框架的火车信息查询插件，可以实时查询中国铁路车次信息和行程详情。


## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests pillow
```

### 2. 部署插件

将 `Ncatbot_train_info` 文件夹复制到你的 Ncatbot5 项目的 `plugins/` 目录下：

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
请勿用于商业用途。

## 🙏 致谢

- [Ncatbot5](https://github.com/ncatbot/NcatBot) - QQ 机器人框架
- [12306](https://www.12306.cn/) - 车次数据源
- [Bilibili@HXD1D0390](https://space.bilibili.com/1171186314/upload/opus) - 火车贴图
- [RAIL.RE](rail.re) - 车型数据源

## 📮 反馈

如有问题或建议，欢迎提交 Issue。

---

**反对直特换桶😡还我原色大列😡**
