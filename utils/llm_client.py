"""大模型API客户端"""
import os
import time
import requests
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class LLMClient:
    """大模型API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat", base_url: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK")
        if not self.api_key:
            raise ValueError("请设置环境变量DEEPSEEK或传入api_key参数")
        
        self.model = model
        self.base_url = base_url or "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 创建带重试机制的session
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["POST"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        self.session = session
    
    def call(self, prompt: str, system_prompt: Optional[str] = None, 
             max_tokens: int = 4096, temperature: float = 0.2, timeout: tuple = (10, 180)) -> str:
        """调用大模型API"""
        messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(3):
            try:
                resp = self.session.post(
                    self.base_url,
                    headers=self.headers,
                    json={"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
                    timeout=timeout
                )
                resp.raise_for_status()
                result = resp.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                raise RuntimeError(f"API返回格式异常: {result}")
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < 2:
                    wait = 2 * (2 ** attempt)
                    print(f"请求失败，{wait}秒后重试 ({attempt + 1}/3)...")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"API调用失败（已重试3次）: {e}")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < 2:
                    time.sleep(2 * (2 ** attempt))
                    continue
                raise RuntimeError(f"API调用失败 (HTTP {e.response.status_code}): {e}")
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

