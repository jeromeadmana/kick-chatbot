# app/ai_client.py
import os
from typing import List, Dict, Optional
from app.core.config import settings
import httpx
import asyncio

class AIClient:
    """
    Minimal AI client wrapper. Supports:
      - OpenAI (official API) if OPENAI_API_KEY present
      - Hugging Face Inference API if HUGGINGFACE_API_KEY present

    For production: add streaming endpoints, error handling, retry/backoff.
    """

    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.hf_key = settings.HUGGINGFACE_API_KEY

    async def generate(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> str:
        """
        messages: list of {"role": "user/system/assistant", "content": "..."}
        Returns assistant text reply.
        """
        if self.openai_key:
            return await self._openai_chat(messages, model)
        if self.hf_key:
            return await self._hf_inference(messages, model)
        raise RuntimeError("No AI provider configured. Set OPENAI_API_KEY or HUGGINGFACE_API_KEY")

    async def _openai_chat(self, messages, model):
        import openai
        openai.api_key = self.openai_key
        # use async to avoid blocking
        loop = asyncio.get_running_loop()
        def request():
            return openai.ChatCompletion.create(model=model, messages=messages, max_tokens=300)
        resp = await loop.run_in_executor(None, request)
        return resp["choices"][0]["message"]["content"].strip()

    async def _hf_inference(self, messages, model):
        # We'll use a simple concatenation strategy for HF text-generation models.
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages]) + "\nassistant:"
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {self.hf_key}"}
            resp = await client.post(url, headers=headers, json={"inputs": prompt, "options": {"use_cache": False}})
            resp.raise_for_status()
            data = resp.json()
            # HF returns different shapes; for text-generation it's often [{"generated_text":"..."}]
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            # generic fallback
            return str(data)
