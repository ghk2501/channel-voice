"""
飞书 API 封装 - 语音文件上传与消息发送
"""

import os
import json
import requests


class FeishuClient:
    """飞书 API 客户端"""

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str, chat_id: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.chat_id = chat_id
        self._token = None

    def _get_tenant_token(self) -> str:
        resp = requests.post(
            f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
        )
        resp.raise_for_status()
        self._token = resp.json()["tenant_access_token"]
        return self._token

    @property
    def token(self) -> str:
        if not self._token:
            self._get_tenant_token()
        return self._token

    def upload_audio(self, audio_path: str, duration_ms: int) -> str:
        with open(audio_path, "rb") as f:
            resp = requests.post(
                f"{self.BASE_URL}/im/v1/files",
                headers={"Authorization": f"Bearer {self.token}"},
                files={
                    "file": (os.path.basename(audio_path), f, "audio/mpeg"),
                },
                data={
                    "file_type": "opus",
                    "file_name": "voice.ogg",
                    "duration": str(duration_ms),
                }
            )
        resp.raise_for_status()
        return resp.json()["data"]["file_key"]

    def send_voice(self, file_key: str) -> dict:
        resp = requests.post(
            f"{self.BASE_URL}/im/v1/messages?receive_id_type=chat_id",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={
                "receive_id": self.chat_id,
                "msg_type": "audio",
                "content": json.dumps({"file_key": file_key}),
            }
        )
        resp.raise_for_status()
        return resp.json()
