"""
飞书 API 封装 - 语音文件上传与消息发送
"""

import os
import json
import time

import requests


class FeishuClient:
    """飞书 API 客户端"""

    BASE_URL = "https://open.feishu.cn/open-apis"
    MAX_RETRIES = 2
    TOKEN_TTL = 7000  # token 有效期 2h，提前 200s 刷新

    def __init__(self, app_id: str, app_secret: str, chat_id: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.chat_id = chat_id
        self._token = None
        self._token_expires_at = 0.0

    def _request_with_retry(self, method, url, **kwargs):
        """带重试的 HTTP 请求"""
        last_exc = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                resp = method(url, **kwargs)
                resp.raise_for_status()
                return resp
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt < self.MAX_RETRIES:
                    time.sleep(1)
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    last_exc = e
                    if attempt < self.MAX_RETRIES:
                        time.sleep(2)
                else:
                    raise
        raise last_exc

    def _get_tenant_token(self) -> str:
        resp = self._request_with_retry(
            requests.post,
            f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=30,
        )
        data = resp.json()
        token = data.get("tenant_access_token")
        if not token:
            raise RuntimeError(f"飞书 token 响应异常: {data}")
        self._token = token
        self._token_expires_at = time.time() + self.TOKEN_TTL
        return self._token

    @property
    def token(self) -> str:
        if not self._token or time.time() >= self._token_expires_at:
            self._get_tenant_token()
        return self._token

    def upload_audio(self, audio_path: str, duration_ms: int) -> str:
        with open(audio_path, "rb") as f:
            resp = self._request_with_retry(
                requests.post,
                f"{self.BASE_URL}/im/v1/files",
                headers={"Authorization": f"Bearer {self.token}"},
                files={
                    "file": (os.path.basename(audio_path), f, "application/octet-stream"),
                },
                data={
                    "file_type": "opus",
                    "file_name": "voice.ogg",
                    "duration": str(duration_ms),
                },
                timeout=60,
            )
        return resp.json()["data"]["file_key"]

    def send_voice(self, file_key: str) -> dict:
        resp = self._request_with_retry(
            requests.post,
            f"{self.BASE_URL}/im/v1/messages?receive_id_type=chat_id",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={
                "receive_id": self.chat_id,
                "msg_type": "audio",
                "content": json.dumps({"file_key": file_key}),
            },
            timeout=30,
        )
        return resp.json()
