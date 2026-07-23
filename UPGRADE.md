# 升级指南

## 从 v0.1.0 升级到 v0.2.0

### 兼容性保证

✅ **完全向后兼容** — 旧版配置可直接使用，无需任何修改
✅ `.env` 文件格式不变，新增字段均为可选
✅ `speak.py` 和 `setup.py` 命令行用法不变

### 升级步骤

#### 方式一：全新部署（推荐）

```bash
# 克隆新版
git clone https://github.com/ghk2501/channel-voice.git
cd channel-voice

# 复制旧版配置
cp /path/to/old/.env .env

# 安装依赖
pip install -r requirements.txt

# 验证
python setup.py check
python speak.py "升级完成，语音消息测试"
```

#### 方式二：原地更新

```bash
# 进到旧版目录
cd /path/to/channel-voice

# 拉取最新代码
git pull origin master

# 安装新增依赖
pip install -r requirements.txt

# 检查配置兼容性
python setup.py check
```

### 配置变更说明

| 字段 | v0.1.0 | v0.2.0 | 备注 |
|------|:------:|:------:|------|
| APP_ID | ✅ | ✅ | 不变 |
| APP_SECRET | ✅ | ✅ | 不变 |
| CHAT_ID | ✅ | ✅ | 不变 |
| TTS_ENGINE | ✅ | ✅ | 不变 |
| VOLC_API_KEY | ✅ | ✅ | 不变 |
| VOLC_SPEAKER | ✅ | ✅ | 不变 |
| CHANNEL | — | ✅ **新增** | 默认 feishu，不填就用飞书 |
| TELEGRAM_BOT_TOKEN | — | ✅ **新增** | 使用 Telegram 时才需要 |
| TELEGRAM_CHAT_ID | — | ✅ **新增** | 使用 Telegram 时才需要 |

> **旧版 `.env` 直接复制到新版就能用，新增字段均有默认值，无需额外配置。**

### 如果升级出问题了

```bash
# 查看当前版本
python -c "from src import __version__; print(__version__)"

# 回滚到旧版
git checkout v0.1.0
pip install -r requirements.txt
```