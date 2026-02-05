# Discord Slash Commands 配置指南

## 📋 概述

本指南将帮助你配置Discord Bot的Slash Commands功能，让你可以在Discord中通过 `/analyze 600519` 这样的命令来触发股票分析。

## 🔑 步骤1：获取Discord Application ID

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 选择你的应用（之前创建Bot时创建的应用）
3. 在左侧菜单点击 **General Information**
4. 复制 **APPLICATION ID**

![Application ID位置](https://i.imgur.com/example.png)

## ⚙️ 步骤2：配置环境变量

编辑 `.env` 文件，找到Discord配置部分，填入你的Application ID：

```env
# Discord Bot 命令接收配置
DISCORD_APPLICATION_ID=你的Application_ID
DISCORD_BOT_TOKEN=你的Bot_Token
DISCORD_MAIN_CHANNEL_ID=你的频道ID
```

## 🚀 步骤3：注册Slash Commands

在项目根目录运行注册脚本：

```bash
# 在Docker外（本地）
python register_discord_commands.py

# 或在Docker内
docker compose -f ./docker/docker-compose.yml exec analyzer python register_discord_commands.py
```

成功后你会看到：

```
==================================================
Discord Slash Commands 注册工具
==================================================

🚀 开始注册Discord Slash Commands...
📱 Application ID: 1234567890
📋 注册 5 个命令

🧹 清理现有命令...

📝 注册新命令...
   ✅ /analyze - 分析指定股票
   ✅ /market - 查看大盘复盘分析
   ✅ /batch - 批量分析配置的自选股列表
   ✅ /help - 显示帮助信息
   ✅ /status - 查看系统状态

==================================================
✅ 成功注册 5/5 个命令
==================================================

🎉 所有命令注册成功！
```

## 🌐 步骤4：配置Interactions Endpoint URL

现在需要告诉Discord你的服务器地址，让它能发送命令到你的应用：

1. 在 Discord Developer Portal 中，选择你的应用
2. 点击左侧的 **General Information**
3. 找到 **INTERACTIONS ENDPOINT URL** 部分
4. 填入你的服务器地址：

```
https://你的域名/bot/discord
```

**重要提示：**
- 必须是 HTTPS（Discord要求）
- 如果使用Docker本地部署，需要使用内网穿透工具（如ngrok）
- 或者部署到有公网IP的服务器

### 使用 ngrok 进行本地测试（推荐）

如果你在本地运行：

```bash
# 1. 安装ngrok (https://ngrok.com/)
# 2. 启动ngrok
ngrok http 8000

# 3. 复制 ngrok 提供的 HTTPS 地址
# 例如：https://abc123.ngrok.io

# 4. 在Discord Developer Portal填入：
https://abc123.ngrok.io/bot/discord
```

5. 点击 **Save Changes**
6. Discord会发送一个验证请求到你的服务器

如果验证成功，你会看到绿色的✅标记！

## 📱 步骤5：测试Slash Commands

在你的Discord服务器中测试命令：

### 可用命令列表：

1. **分析股票**
   ```
   /analyze 600519
   /analyze AAPL
   /analyze hk09618
   ```

2. **大盘复盘**
   ```
   /market
   ```

3. **批量分析**
   ```
   /batch
   ```

4. **帮助信息**
   ```
   /help
   ```

5. **系统状态**
   ```
   /status
   ```

## ⚠️ 常见问题

### Q1: 命令在Discord中看不到？
A: Slash Commands需要1-5分钟才能同步。如果超过5分钟还看不到：
- 尝试退出并重新加入服务器
- 确认Bot有 `applications.commands` 权限
- 重新注册命令：`python register_discord_commands.py`

### Q2: 点击命令后没有响应？
A: 检查以下几点：
- WebUI服务是否正常运行（`docker compose ps`）
- Interactions Endpoint URL是否正确配置
- 查看Docker日志：`docker compose logs analyzer`

### Q3: Discord返回"The application did not respond"？
A: 这是因为：
- 服务器没有在3秒内响应Discord
- Interactions Endpoint URL配置错误
- 防火墙阻止了Discord的请求

### Q4: 签名验证失败？
A: 需要配置Public Key：
1. 在Discord Developer Portal的General Information页面
2. 复制 **PUBLIC KEY**
3. 添加到 `.env`：
   ```env
   DISCORD_PUBLIC_KEY=你的Public_Key
   ```

## 🔒 安全建议

1. **永远不要**将 `DISCORD_BOT_TOKEN` 提交到Git
2. 使用环境变量管理敏感信息
3. 定期轮换Bot Token
4. 启用Discord的签名验证

## 📚 相关文档

- [Discord Interactions](https://discord.com/developers/docs/interactions/receiving-and-responding)
- [Discord Slash Commands](https://discord.com/developers/docs/interactions/application-commands)
- [Discord Developer Portal](https://discord.com/developers/applications)

## 💡 下一步

配置完成后，你可以：
- 在Discord中使用 `/analyze` 命令分析股票
- 使用 `/market` 命令查看大盘复盘
- 使用 `/batch` 命令批量分析自选股

祝使用愉快！🎉
