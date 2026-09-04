import os, random, time, requests

class LLMOrchestrator:
    """Provider fallback chain with explicit 429 backoff and 413 chunk reduction."""
    def __init__(self):
        self.providers = [("gemini", os.getenv("GEMINI_API_KEY")), ("groq", os.getenv("GROQ_API_KEY")), ("deepseek", os.getenv("DEEPSEEK_API_KEY"))]

    @staticmethod
    def chunk_text(text, max_chars=12000):
        text = text or ""
        return [text[i:i+max_chars] for i in range(0, len(text), max_chars)] or [""]

    @staticmethod
    def _request(url, headers, payload, retries=4):
        last = None
        for attempt in range(retries):
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=45)
                if r.status_code == 413:
                    raise ValueError("PAYLOAD_TOO_LARGE")
                if r.status_code == 429:
                    time.sleep(min(30, (2 ** attempt) + random.random()))
                    continue
                r.raise_for_status()
                return r.json()
            except ValueError:
                raise
            except requests.RequestException as e:
                last = e
                if attempt < retries - 1:
                    time.sleep(min(15, (2 ** attempt) + random.random()))
        raise RuntimeError(str(last) if last else "request failed")

    def _call(self, provider, key, chunk):
        if provider == "gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + key
            data = self._request(url, {"Content-Type":"application/json"}, {"contents":[{"parts":[{"text":chunk}]}]})
            return data["candidates"][0]["content"]["parts"][0]["text"]
        if provider == "groq":
            data = self._request("https://api.groq.com/openai/v1/chat/completions", {"Authorization":"Bearer "+key}, {"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":chunk}]})
            return data["choices"][0]["message"]["content"]
        data = self._request("https://api.deepseek.com/chat/completions", {"Authorization":"Bearer "+key}, {"model":"deepseek-chat","messages":[{"role":"user","content":chunk}]})
        return data["choices"][0]["message"]["content"]

    def extract(self, text):
        last_error = None
        for provider, key in self.providers:
            if not key:
                continue
            try:
                chunks = self.chunk_text(text)
                try:
                    out = [self._call(provider, key, c) for c in chunks]
                except ValueError as e:
                    if str(e) != "PAYLOAD_TOO_LARGE":
                        raise
                    smaller = self.chunk_text(text, 6000)
                    out = [self._call(provider, key, c) for c in smaller]
                return {"provider": provider, "text": "\n".join(out)}
            except Exception as e:
                last_error = e
        return {"provider": None, "text": "", "error": str(last_error) if last_error else "No provider key configured"}
