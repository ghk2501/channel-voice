# Channel Voice 部署引导 — AI Agent 执行手册

AI Agent 按此文档步骤引导用户完成配置。

## 第一步：了解用户需求

向用户说明：这个工具能让你的 AI Agent 通过飞书发送语音消息。

支持的 TTS 供应商：

| 供应商 | 费用 | 音质 | 推荐场景 |
|--------|------|------|----------|
| Edge-TTS（微软） | 免费 | 一般 | 快速测试、零预算 |
| 火山引擎（豆包语音） | 按量计费 | 优秀 | 追求音质、中文场景 |

## 第二步：配置飞书应用

核心就是三个值：**APP_ID**、**APP_SECRET**、**CHAT_ID**

问用户：**你已经有飞书应用了吗？**

**已有应用：**
- 打开 https://open.feishu.cn/app → 点开已有应用
- 「凭证与基础信息」→ 复制 **App ID** 和 **App Secret**

**新建应用：**
- 打开 https://open.feishu.cn/app
- 点「创建企业自建应用」→ 填名称创建
- 「凭证与基础信息」→ 复制 **App ID** 和 **App Secret**
- 默认权限就够用，无需额外配置

**获取 CHAT_ID：**
1. 在飞书中建个群（或用已有群）
2. 群设置 → 添加机器人 → 选择刚创建的应用
3. 群里发条消息
4. 获取 Chat ID：
   ```bash
   # 获取 token
   curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
     -H 'Content-Type: application/json' \
     -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
   
   # 获取群列表，找到目标群的 chat_id（oc_ 开头）
   curl 'https://open.feishu.cn/open-apis/im/v1/chats' \
     -H 'Authorization: Bearer <TOKEN>'
   ```

AI 自动写入：
```bash
python setup.py write APP_ID=cli_xxx
python setup.py write APP_SECRET=xxx
python setup.py write CHAT_ID=oc_xxx
```

## 第三步：配置 TTS 供应商

### 选项 A：Edge-TTS（免费，无需注册）

无需任何凭证，直接设置引擎即可：

```bash
python setup.py write TTS_ENGINE=edge-tts
python setup.py write EDGE_TTS_VOICE=zh-CN-XiaoyiNeural
```

### 选项 B：火山引擎（推荐）

引导用户：

1. 打开 https://console.volcengine.com/speech
2. 左侧「语音合成」→「应用管理」→ 创建应用
3. 获取 **x-api-key**
4. 在「音色列表」中选一个音色，记下音色 ID

AI 自动写入：

```bash
python setup.py write TTS_ENGINE=volc
python setup.py write VOLC_API_KEY=用户提供的key
python setup.py write VOLC_RESOURCE_ID=seed-tts-2.0
python setup.py write VOLC_SPEAKER=用户选的音色ID
```

## 第四步：配置 FFmpeg

```bash
# 若 ffmpeg 在系统 PATH 中
python setup.py write FFMPEG_PATH=ffmpeg

# Windows 用户下载 ffmpeg.exe 后
python setup.py write FFMPEG_PATH=C:\path\to\ffmpeg.exe
```

## 第五步：验证

```bash
# 检查配置完整性
python setup.py check

# 测试 TTS 引擎
python setup.py test

# 完整流程：生成 → 转码 → 发送飞书
pip install -r requirements.txt
python speak.py "配置完成，语音消息已上线"
```

确认飞书群收到语音消息 → 告诉用户配置完成。
