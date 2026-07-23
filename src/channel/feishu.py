"""
Feishu/Lark Channel - Voice message upload and send
"""

import os
import json
import time
import requests
from .base import ChannelBase


class FeishuChannel(ChannelBase):
    """Feishu/Lark voice message channel"""
    name = "feishu"
    BASE_URL = "https://open.feishu.cn/open-apis"
    MAX_RETRIES = 2
    TOKEN_TTL = 7000

    def __init__(self, app_id, app_secret, chat_id):
        self.app_id = app_id
        self.app_secret = app_secret
        self.chat_id = chat_id
        self._token = None
        self._token_expires_at = 0.0

    def _request_with_retry(self, method, url, **kwargs):
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

    def _get_tenant_token(self):
        resp = self._request_with_retry(
            requests.post,
            f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=30,
        )
        data = resp.json()
        token = data.get("tenant_access_token")
        if not token:
            raise RuntimeError(f"Feishu token error: {data}")
        self._token = token
        self._token_expires_at = time.time() + self.TOKEN_TTL
        return self._token

    @property
    def token(self):
        if not self._token or time.time() >= self._token_expires_at:
            self._get_tenant_token()
        return self._token

    def upload_audio(self, audio_path, duration_ms):
        with open(audio_path, "rb") as f:
            resp = self._request_with_retry(
                requests.post,
                f"{self.BASE_URL}/im/v1/files",
                headers={"Authorization": f"Bearer {self.token}"},
                files={"file": (os.path.basename(audio_path), f, "application/octet-stream")},
                data={"file_type": "opus", "file_name": "voice.ogg", "duration": str(duration_ms)},
                timeout=60,
            )
        return resp.json()["data"]["file_key"]

    def send_voice(self, audio_path, duration_ms):
        file_key = self.upload_audio(audio_path, duration_ms)
        resp = self._request_with_retry(
            requests.post,
            f"{self.BASE_URL}/im/v1/messages?receive_id_type=chat_id",
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            json={"receive_id": self.chat_id, "msg_type": "audio", "content": json.dumps({"file_key": file_key})},
            timeout=30,
        )
        return True

    def validate_config(self):
        missing = []
        if not self.app_id:
            missing.append("APP_ID")
        if not self.app_secret:
            missing.append("APP_SECRET")
        if not self.chat_id:
            missing.append("CHAT_ID")
        return missing
