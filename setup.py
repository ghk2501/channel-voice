#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Echo Voice 部署助手 - AI Agent 调用的配置工具

用法:
  python setup.py providers          # 列出可用供应商
  python setup.py guide <provider>   # 查看供应商配置引导
  python setup.py write <key>=<val>  # 写入 .env 配置项
  python setup.py check              # 检查 .env 配置完整性
  python setup.py test               # 测试当前配置是否能生成语音
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.provider import PROVIDERS, get_provider
from src.config import get_config


ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _ensure_env():
    """确保 .env 文件存在"""
    if not os.path.exists(ENV_PATH):
        example = ENV_PATH + ".example"
        if os.path.exists(example):
            with open(example, encoding="utf-8") as f:
                content = f.read()
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[setup] 已从 .env.example 创建 .env")
        else:
            print(f"[setup] 错误: 找不到 .env.example", file=sys.stderr)
            sys.exit(1)


def cmd_providers():
    """列出所有可用供应商"""
    print("\n可用的 TTS 供应商:\n")
    for p in PROVIDERS:
        print(f"  [{p['id']}] {p['name']}")
        print(f"        {p['description']}")
        print(f"        推荐: {' / '.join(p['recommend_for'])}")
        print()


def cmd_guide(provider_id: str):
    """显示供应商配置引导"""
    p = get_provider(provider_id)
    if not p:
        print(f"[setup] 未知供应商: {provider_id}", file=sys.stderr)
        print(f"        可用: {', '.join(x['id'] for x in PROVIDERS)}")
        sys.exit(1)

    print(f"\n  {p['name']} 配置引导\n")
    print(f"  {p['description']}\n")
    print("  --- 优点 ---")
    for pro in p["pros"]:
        print(f"    + {pro}")
    print("  --- 缺点 ---")
    for con in p["cons"]:
        print(f"    - {con}")

    print("\n  --- 需要的信息 ---")
    for field in p["credential_fields"]:
        print(f"    {field['label']}")
        if "default" in field:
            print(f"    默认值: {field['default']}")
        print(f"    {field['hint']}")
        if "doc_url" in field:
            print(f"    获取地址: {field['doc_url']}")
        print()

    print("  --- 配置步骤 ---")
    for step in p["setup_steps"]:
        print(f"    {step}")
    print()


def cmd_write(key_val: str):
    """写入 .env 配置项"""
    _ensure_env()

    if "=" not in key_val:
        print(f"[setup] 格式错误: 请使用 key=value 格式", file=sys.stderr)
        sys.exit(1)

    key, value = key_val.split("=", 1)
    key = key.strip()
    value = value.strip()

    lines = []
    found = False
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(f"{key}=") or line.startswith(f"# {key}="):
                lines.append(f"{key}={value}\n")
                found = True
            else:
                lines.append(line)

    if not found:
        lines.append(f"\n{key}={value}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[setup] 已设置 {key}={value}")


def cmd_check():
    """检查 .env 配置完整性"""
    _ensure_env()
    cfg = get_config(ENV_PATH)
    missing = cfg.validate()

    if missing:
        print(f"\n[setup] 缺少以下配置项:\n")
        for m in missing:
            print(f"  - {m}")
        print(f"\n请使用 python setup.py write {m}=<值> 逐个填写")
        print(f"或联系 AI 引导获取\n")
    else:
        print(f"[setup] 配置完整，可以开始使用了！")
        print(f"       TTS 引擎: {cfg.tts_engine}")
        if cfg.tts_engine == "volc":
            print(f"       Resource: {cfg.volc_resource_id}")
            print(f"       音色: {cfg.volc_speaker}")


def cmd_test():
    """测试配置是否能生成语音"""
    _ensure_env()
    cfg = get_config(ENV_PATH)
    missing = cfg.validate()
    if missing:
        print(f"[setup] 配置不完整，缺少: {', '.join(missing)}")
        print(f"请先完成配置再测试")
        sys.exit(1)

    import asyncio
    from src.tts import create_engine

    tts = create_engine(cfg)
    tmp = os.path.join(os.path.dirname(ENV_PATH), ".test_output.mp3")

    print(f"[setup] 测试 {tts.name} 引擎...")
    success = asyncio.run(tts.synthesize("这是一条测试语音，配置正确。", tmp))

    if success and os.path.getsize(tmp) > 100:
        print(f"[setup] 测试通过！生成了 {os.path.getsize(tmp) / 1024:.0f}KB 音频")
        os.remove(tmp)
    else:
        print(f"[setup] 测试失败")
        if os.path.exists(tmp):
            os.remove(tmp)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "providers":
        cmd_providers()
    elif cmd == "guide":
        if len(sys.argv) < 3:
            print("[setup] 请指定供应商 ID，如: python setup.py guide volc")
            sys.exit(1)
        cmd_guide(sys.argv[2])
    elif cmd == "write":
        if len(sys.argv) < 3:
            print("[setup] 请指定 key=value，如: python setup.py write VOLC_API_KEY=xxx")
            sys.exit(1)
        cmd_write(sys.argv[2])
    elif cmd == "check":
        cmd_check()
    elif cmd == "test":
        cmd_test()
    else:
        print(f"[setup] 未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
