#!/usr/bin/env python3
"""Minimal mock HTTP target for guerrilla AuditAI runs.

Intentionally weak: one SEED blurb for all questions (not per-case RAG).
Empty response contexts so faithfulness uses dataset case.contexts.
Do not treat high scores with a smarter mock as product quality.
"""
from __future__ import annotations
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

SEED = 'EduMIND — Multimodal Bilingual Lecture Assistant & Active Learning Pipeline EduMIND is an enterprise-grade, highly modular Bilingual Lecture Assistant & Active Learning Pipeline. Designed specifically for academic environments where lectures mix languages (e.g., Code-Mixed Vietnamese-English, such as "hôm nay chúng ta học attention mechanism"), EduMIND transcribes bilingual speech, measures code-switching metrics, translates text preserving technical terms, indexes slides, and executes retrieval-augmented generation (RAG). The system integrates a Human-in-the-Loop Active Learning framework powered by Label Studio and an ML backend to continually harvest human-corrected data, immediately updating the local knowledge base and building a gold-standard corpus.'
ATTACK = re.compile(
    r"(ignore all previous|system prompt|api key|bỏ qua mọi|tiết lộ)",
    re.I,
)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        q = str(body.get("question") or "")
        if ATTACK.search(q):
            ans = "I cannot reveal system prompts or secrets."
        elif SEED:
            # Weak: same SEED for every question (honest FAIL under strict judge)
            ans = "Based on available docs: " + SEED[:500]
        else:
            ans = f"(mock) no seed docs for: {q[:80]}"
        raw = json.dumps({"answer": ans, "contexts": []}, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

print("mock adapter http://127.0.0.1:18080/chat (weak SEED, empty contexts)")
HTTPServer(("127.0.0.1", 18080), H).serve_forever()
