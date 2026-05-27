# Echo Voice

让不支持语音消息的 AI Agent 频道（飞书等）拥有 TTS 语音播报能力。

---

## 如果你是 AI Agent（Claude Code 等），请读这里

用户发这个链接给你，是想让你帮他配置语音播报。按以下流程执行。

### 先确认

问用户：

1. **想用哪个 TTS 供应商？**
   - **推荐火山引擎**（豆包语音大模型，抖音同款音质，中文效果顶级）
   - 也可以用 Edge-TTS（微软免费，无需注册，开箱即用但音色少）

2. **飞书应用的凭证？**
   - **已有应用** → 去 https://open.feishu.cn/app → 找到应用 → 「凭证与基础信息」拿 App ID 和 App Secret
   - **没有应用** → 按下方「飞书配置详细步骤」新建
   - 两种都需要 CHAT_ID（机器人所在群聊的 ID）

3. **FFmpeg 路径？**
   - 默认 `ffmpeg`（在系统 PATH 中则无需配置）
   - Windows 用户可下载 ffmpeg.exe 放在项目目录

### 执行

按顺序执行：

```bash
# 查看可选供应商
python setup.py providers

# 用户选择后，引导获取凭证，自动写入
python setup.py write TTS_ENGINE=volc
python setup.py write VOLC_API_KEY=用户的key
python setup.py write VOLC_SPEAKER=用户选的音色ID
python setup.py write APP_ID=用户的飞书AppID
python setup.py write APP_SECRET=用户的飞书Secret
python setup.py write CHAT_ID=用户的飞书群ChatID

# 检查配置完整性
python setup.py check

# 测试 TTS 是否能生成音频
python setup.py test

# 完整测试：生成语音 → 转码 → 发送飞书
python speak.py "配置完成，语音播报已上线"
```

确认飞书群里收到了语音消息，告诉用户：**配置完成，以后在频道里可直接发送语音消息。**

### 飞书配置详细步骤

引导用户：

1. 打开 https://open.feishu.cn/app ，点击「创建企业自建应用」
2. 填写应用名称，创建
3. 在左侧「凭证与基础信息」中，拿到 **App ID** 和 **App Secret**
4. 在左侧「权限管理」→ 搜索并开启 `im:message:send_as_bot`（发送消息权限）
5. 在左侧「安全设置」→ 设置 IP 白名单为 `0.0.0.0/0`（或留空）
6. 点击「版本管理与发布」→ 创建版本 → 提交发布 → 等待管理员审批
7. 在飞书中创建一个群聊，进入群设置 → 机器人 → 添加机器人 → 选择刚创建的应用
8. 在群中发一条任意消息
9. 用以下命令获取 Chat ID：
   ```bash
   # 获取 token
   curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
     -H 'Content-Type: application/json' \
     -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
   
   # 获取群列表，找到目标群的 chat_id（以 oc_ 开头）
   curl 'https://open.feishu.cn/open-apis/im/v1/chats' \
     -H 'Authorization: Bearer <TOKEN>'
   ```

### 火山引擎配置

引导用户：

1. 打开 https://console.volcengine.com/speech ，注册/登录
2. 在左侧菜单选择「语音合成」→「应用管理」
3. 点击「创建应用」，填写名称，创建
4. 在应用详情页找到 **x-api-key**
5. 在「音色列表」中查看可用音色，选一个喜欢的（如 `zh_female_vv_uranus_bigtts` / `saturn_zh_female_keainvsheng_tob` 等）
6. 将信息填入 `.env`

---

## 如果你是人类，请读这里

### 这是什么

一个让 AI Agent 能通过飞书发送语音消息的工具。

工作流程：`文字 → TTS(生成MP3) → FFmpeg(转码Opus) → 飞书API(发送语音消息)`

### 快速开始

```bash
pip install -r requirements.txt
# 把 .env.example 复制为 .env，填好配置
python speak.py "你好，世界"
```

### 文件说明

| 文件 | 用途 |
|------|------|
| `speak.py` | 入口脚本：文字 → 语音 → 发送飞书 |
| `setup.py` | 部署助手：AI 自动配置工具 |
| `src/tts.py` | TTS 引擎（Edge-TTS / 火山引擎） |
| `src/feishu.py` | 飞书 API 封装 |
| `src/config.py` | 配置管理 |
| `src/provider.py` | 供应商注册表 |
| `.env.example` | 配置模板（复制为 .env 并填写） |
| `SETUP_GUIDE.md` | 详细部署引导 |

### 依赖

- Python 3.8+
- FFmpeg（音频转码）
- 网络连接
