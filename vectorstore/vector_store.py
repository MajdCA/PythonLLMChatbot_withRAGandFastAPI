import os
import json
import requests
import numpy as np
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, store_path: str, ollama_url: str = None, embed_model: str = None):
        self.store_path = store_path
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://192.168.1.253:11435")
        self.embed_model = embed_model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")
        self.records: List[Dict[str, Any]] = []
        if os.path.exists(self.store_path):
            self._load()

    def _load(self):
        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "records" in data:
                self.records = data["records"]
            elif isinstance(data, list):
                self.records = data
            else:
                self.records = []
        except Exception:
            self.records = []

    def save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        payload = {"model": self.embed_model, "records": self.records}
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def embed(self, text: str) -> np.ndarray:
        resp = requests.post(
            f"{self.ollama_url}/api/embeddings",
            json={"model": self.embed_model, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        emb = resp.json().get("embedding")
        if emb is None:
            raise RuntimeError("No embedding returned from Ollama embeddings API.")
        return np.array(emb, dtype=np.float32)

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        metadatas = metadatas or [{}] * len(texts)
        new_records = []
        for i, t in enumerate(texts):
            if not t or not t.strip():
                continue
            vec = self.embed(t)
            new_records.append({
                "text": t,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "embedding": vec.tolist(),
            })
        self.records.extend(new_records)
        self.save()

    def search(self, query: str, top_k: int = 5):
        if not self.records:
            return []
        q = self.embed(query)
        q_norm = float(np.linalg.norm(q) + 1e-8)
        scored = []
        for rec in self.records:
            v = np.array(rec["embedding"], dtype=np.float32)
            denom = (np.linalg.norm(v) + 1e-8) * q_norm
            score = float(np.dot(q, v) / denom)
            scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def search_context(self, query: str, top_k: int = 5) -> str:
        hits = self.search(query, top_k=top_k)
        parts = []
        for score, rec in hits:
            src = rec.get("metadata", {}).get("source", "source")
            parts.append(f"[{src}] {rec['text']}")
        return "\n\n".join(parts)
