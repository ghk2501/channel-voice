"""
TTS 供应商注册表 — AI Agent 用来自动推荐和引导配置
"""

PROVIDERS = [
    {
        "id": "edge-tts",
        "name": "Edge-TTS（微软免费）",
        "tagline": "免费，无需注册，开箱即用",
        "description": "微软提供的免费 TTS 服务，无需注册账号，装好依赖就能用。",
        "pros": ["免费", "无需注册", "开箱即用", "多语言支持"],
        "cons": ["中文音色少（仅4个）", "音质一般", "不可定制"],
        "best_for": ["快速测试", "预算为零", "对音质要求不高"],
        "price": "免费",
        "credential_fields": [],
        "guide_steps": ["无需注册，直接使用"],
        "config_prompt": "推荐使用 zh-CN-XiaoyiNeural（温暖女声）或 zh-CN-XiaoyiNeural（活泼女声）",
    },
    {
        "id": "volc",
        "name": "火山引擎 TTS（豆包语音大模型）",
        "tagline": "中文效果顶级，抖音同款音质",
        "description": "字节跳动出品的豆包语音大模型，中文语音合成效果业界领先。",
        "pros": ["中文效果极好", "音色丰富（通用+角色扮演）", "响应快", "支持情感控制"],
        "cons": ["需要注册账号", "按量计费", "需联网"],
        "best_for": ["追求音质", "中文场景为主", "生产环境", "角色扮演"],
        "price": "按字符计费，新用户有免费额度",
        "credential_fields": [
            {
                "key": "VOLC_API_KEY",
                "label": "x-api-key（API密钥）",
                "hint": "控制台 → 语音合成 → 应用管理 → 创建/查看应用",
                "doc_url": "https://console.volcengine.com/speech",
                "placeholder": "示例: 33acab00-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            },
            {
                "key": "VOLC_RESOURCE_ID",
                "label": "Resource ID",
                "default": "seed-tts-2.0",
                "options": [
                    {"value": "seed-tts-2.0", "desc": "语音合成2.0字符版（推荐）"},
                    {"value": "seed-tts-1.0", "desc": "语音合成1.0字符版"},
                ],
            },
            {
                "key": "VOLC_SPEAKER",
                "label": "音色 ID",
                "hint": "控制台「音色列表」中查看，有通用场景和角色扮演两类",
                "doc_url": "https://console.volcengine.com/speech",
                "examples": [
                    "zh_female_vv_uranus_bigtts — vivi 2.0（通用女声）",
                    "zh_female_xiaohe_uranus_bigtts — 小何（通用女声）",
                    "saturn_zh_female_keainvsheng_tob — 可爱女生（角色扮演）",
                    "saturn_zh_female_cancan_tob — 知性灿灿（角色扮演）",
                    "saturn_zh_female_tiaopigongzhu_tob — 调皮公主（角色扮演）",
                ],
            },
        ],
        "guide_steps": [
            "1. 打开 https://console.volcengine.com/speech 注册/登录",
            "2. 左侧菜单「语音合成」→「应用管理」",
            "3. 点击「创建应用」，填写应用名称",
            "4. 创建后，在应用详情页复制 x-api-key",
            "5. 在「音色列表」浏览可用音色，选一个喜欢的",
            "6. 将 x-api-key 和音色 ID 提供给 AI",
        ],
    },
]


def get_provider(provider_id: str):
    for p in PROVIDERS:
        if p["id"] == provider_id:
            return p
    return None


def recommend(user_input: str = ""):
    """根据用户输入推荐供应商"""
    t = user_input.lower()
    if not t or any(kw in t for kw in ["推荐", "哪个好", "选择"]):
        return get_provider("volc")  # 默认推荐火山引擎
    if any(kw in t for kw in ["免费", "简单", "测试", "不用注册", "省钱"]):
        return get_provider("edge-tts")
    if any(kw in t for kw in ["音质", "好听", "中文", "专业", "生产", "角色"]):
        return get_provider("volc")
    return get_provider("volc")
