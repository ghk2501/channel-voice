---
description: 给 AI Agent 频道增加 TTS 语音消息能力。AI 引导用户选择供应商、获取飞书和 TTS 凭证、自动写入配置、测试发语音。Let Agent Speak In Channel.
---

# Channel Voice — AI 语音消息推送部署 Skill

## 触发场景

用户说以下内容时触发：
- "让我的 Agent 能说话/发语音"
- "给频道加语音播报"
- "配置语音/TTS"
- 发来本项目链接

## 执行流程

### 1. 确认需求

向用户说明功能，询问三个问题：

**① 用哪个 TTS？**
- 推荐火山引擎（音质好，中文顶级）
- 或用 Edge-TTS（免费，无需注册）
- 用户无偏好则默认推荐火山引擎

**② 飞书应用配好了吗？**
- 没有 → 按 SETUP_GUIDE.md 的飞书配置步骤一步步引导
- 已有 → 让用户提供 APP_ID、APP_SECRET、CHAT_ID

**③ FFmpeg 在哪？**
- 默认 `ffmpeg` 即可
- Windows 用户可能需要下载

### 2. 自动配置

获取到信息后，用 setup.py 逐项写入：

```bash
# 飞书
python setup.py write APP_ID=<用户提供的值>
python setup.py write APP_SECRET=<用户提供的值>
python setup.py write CHAT_ID=<用户提供的值>

# TTS 引擎
python setup.py write TTS_ENGINE=<用户选择>
python setup.py write VOLC_API_KEY=<火山引擎key>  # 仅volc
python setup.py write VOLC_SPEAKER=<音色ID>        # 仅volc
```

不用让用户手动编辑文件，AI 全自动完成。

### 3. 验证

```bash
python setup.py check
python setup.py test
pip install -r requirements.txt
python speak.py "配置完成，语音消息已上线"
```

### 4. 告知

确认飞书群收到语音后，告诉用户：
> 配置完成！以后你的 Agent 可以直接在频道里发送语音消息了。
> 如需更换音色，改 .env 里的 VOLC_SPEAKER 即可。
