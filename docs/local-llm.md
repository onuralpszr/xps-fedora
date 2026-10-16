# 🧳 Offline LLM on 32 GB: agents without hurting the desktop

What fits on the Dell XPS 16 DA16260 (32 GB unified memory, Arc B390, NPU 5010) for offline use, for example [Hermes Agent](https://hermes-agent.nousresearch.com/) on a plane. Measured on 2026-10-11 and 2026-10-12 on battery (`xps-ptl-balanced-battery`) unless noted, llama-cpp b11513 with Vulkan, OpenVINO 2026.4.1.

## 🏁 Summary

| Use | Model | Memory | Speed |
| --- | --- | --- | --- |
| 🤖 Agent (Hermes, 64K context) | **gpt-oss-20b** MXFP4 | 13.2 GB | first Hermes reply in 37 s, then 27 tokens/s |
| 📚 Long answers, teaching | **Qwen3-30B-A3B-Instruct-2507** | 15 to 23 GB | 45 tokens/s on a short context |
| 💻 Coding specialist (not measured yet) | Qwen3-Coder-30B-A3B-Instruct | like Qwen3-30B | |

`tools/ai-local/ai-local` starts and stops these as a user service (copy it to `~/.local/bin`; it looks for models in `~/models/gguf`, or `$AI_LOCAL_MODELS`):

```bash
ai-local start gpt-oss       # Hermes default, 64K context
ai-local start qwen30b-chat  # Qwen3-30B with 16K context, for the web chat at http://127.0.0.1:8080
ai-local status              # model, GPU memory, free RAM
ai-local stop
```

## 🧠 Memory: the GPU shares the 32 GB

- **The GPU can use at most 23.18 GiB.** Mesa's Vulkan driver (ANV) gives the integrated GPU a heap of three quarters of system RAM (`vulkaninfo`, `memoryHeaps[0]`). Model, KV cache and compute buffers must fit in it.
- **Hermes needs at least 64,000 tokens of context.** It is a hard check (`MINIMUM_CONTEXT_LENGTH` in Hermes), so the KV cache cannot simply be shrunk.
- **Qwen3-30B-A3B with 64K context** (IQ4_XS, 16-bit cache) takes 22.7 GB of GPU memory. It runs, but left 1.3 GB available and pushed about 5.5 GB of the desktop to swap. Q4_K_M plus that cache does not fit at all (`ErrorOutOfDeviceMemory`).
- **gpt-oss-20b with 64K context** takes 13.2 GB: half its layers use a 128-token sliding window, so its cache is small. During a Hermes run, available RAM stayed above 7.6 GB with Chrome and VS Code open, and nothing went to swap.
- **After unloading, the `xe` driver keeps freed pages in a pool** (`GPUReclaim` in `/proc/meminfo`, 14 GB after the 30B model). The kernel takes them back under pressure, but `free` does not count them as available.
- `tools/ai-local/ai-load-monitor.py` prints each process's GPU memory and GPU time, NPU busy time and memory, and available RAM once a second, without root.

## ⚡ KV cache and flash attention on this GPU

Qwen3-30B-A3B IQ4_XS, `llama-bench`, 512 prompt and 64 generated tokens with 14K tokens already in the context (about Hermes's first prompt):

| KV cache | Flash attention | Reading | Writing |
| --- | :---: | ---: | ---: |
| 8-bit | on | 66 tokens/s | 2 tokens/s |
| 8-bit K, 16-bit V | off | 19 tokens/s | 1.3 tokens/s |
| 16-bit | on | 63 tokens/s | 26 tokens/s |
| **16-bit** | **off** | **175 tokens/s** | **23 tokens/s** |

gpt-oss-20b at the same depth: 309 / 28 tokens/s with flash attention off, 200 / 25 with it on. On Vulkan here, a quantized KV cache and flash attention both slow down sharply as the context grows, so `ai-local` uses a 16-bit cache with `-fa off`. That is why the KV cache costs memory instead of being quantized.

## 🚫 What did not work for Qwen3-30B-A3B

| Path | Result |
| --- | --- |
| OpenVINO GenAI on the GPU (int4) | out of memory: the GPU upload briefly needs about twice the 16 GB model |
| OpenVINO GenAI on the NPU | still compiling after 15 minutes (MoE), stopped |
| llama.cpp Vulkan, Q4_K_M | 717 tokens/s reading, 45 tokens/s writing on an empty context, tool calls work with `--jinja` |

## 🖥️ Effect on the desktop

During a Hermes reply `llama-server` keeps the GPU 100 % busy for the length of the reply (about 28 s for the first one) and idle in between; CPU stays near 10 %. The memory budget is what decides whether the desktop stays usable: keep the server's GPU memory well under the 23 GiB heap and leave several GB available for the browser.

## 🔌 Hermes Agent settings

Back up `~/.hermes/config.yaml`, then point the `model:` section at the local server:

```yaml
model:
  default: "gpt-oss-20b"
  provider: "custom"
  base_url: "http://127.0.0.1:8080/v1"
```

The model name must match `--alias` in `ai-local`. Restore the backup to go back to a hosted model.
