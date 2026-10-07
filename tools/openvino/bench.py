#!/usr/bin/env python3
"""Run one prompt through an OpenVINO GenAI LLM on CPU / GPU / NPU and
report load time, time to first token and decode speed.

Usage: .venv/bin/python bench.py [model_dir] [DEVICE ...]
"""
import sys
import time

import openvino_genai as og

model = sys.argv[1] if len(sys.argv) > 1 else "models/Phi-3.5-mini-instruct-int4-cw-ov"
devices = sys.argv[2:] or ["NPU", "GPU", "CPU"]
prompt = "Explain in three sentences what an NPU is and why laptops have one."

for device in devices:
    t0 = time.perf_counter()
    # NPU compiles the model on first load; the cache makes later loads fast
    pipe = og.LLMPipeline(model, device, CACHE_DIR=".ovcache")
    load = time.perf_counter() - t0

    cfg = og.GenerationConfig(max_new_tokens=128)
    res = pipe.generate([prompt], cfg)
    m = res.perf_metrics

    print(f"\n=== {device} ===")
    print(res.texts[0].strip())
    print(f"-- load {load:.1f}s | first token {m.get_ttft().mean:.0f} ms"
          f" | {m.get_throughput().mean:.1f} tok/s"
          f" | {m.get_num_generated_tokens()} tokens")
    del pipe
