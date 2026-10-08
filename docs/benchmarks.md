# 📊 Local AI benchmarks

Measured on 2026-10-08 on the Dell XPS 16 DA16260 (Core Ultra X7 358H, Arc B390, NPU 5010, 32 GB), plugged in, `xps-ptl-performance` profile, Fedora 45 with the packages from this repository: llama-cpp b11460, OpenVINO and OpenVINO GenAI 2026.4.1, intel-npu-driver 1.38, whisper-cpp 1.9.5, ollama 0.40.1.

## 🏁 Summary

| | Best choice | Why |
| --- | --- | --- |
| 💬 Chat speed (tokens/s) | llama.cpp **Vulkan**, or OpenVINO GenAI on the GPU | 35 to 40 tokens/s for 4B models, 20 to 23 for 9B, 37 for gpt-oss-20b |
| 📄 Long prompts | llama.cpp **OpenVINO GPU** | reads prompts 2 to 3 times faster than Vulkan (Gemma 4 E4B: 4128 against 1433 tokens/s) |
| 🔋 On battery, GPU free | **NPU** with OpenVINO GenAI and `*-cw-ov` models | Qwen3 8B at 23 tokens/s, Phi-3.5 at 39 tokens/s |
| 🦙 Easiest setup | **Ollama** with `ollama-vulkan` | as fast as llama.cpp on the same GGUF, with model downloads and a simple API |
| 🎙️ Speech to text | whisper.cpp **Vulkan** | large-v3-turbo transcribes 66 s of audio in 7.8 s |
| 🔎 Embeddings | llama.cpp **Vulkan** | embeddinggemma-2 at 138 sentences/s, same results as CPU |

## 🦙 llama.cpp

`llama-bench`, 512 prompt tokens (pp512) and 128 generated tokens (tg128), tokens/s. CPU uses 16 threads for prompts and the better of 8 or 16 for generation. OpenVINO GPU uses `GGML_OPENVINO_STATEFUL_EXECUTION=1 -fa 1`.

| Model | CPU pp / tg | Vulkan pp / tg | OpenVINO GPU pp / tg | OpenVINO NPU pp / tg |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.2 1B Q4_0 | 488 / 92 | 5418 / 127 | 17119 / 120 | 3018 / 63 ¹ |
| Qwen3.5 4B Q4_K_M | 96 / 15 | 1407 / 35 | 2708 / 28 | ✗ ² |
| Qwen3.5 4B Q4_0 | 118 / 23 ³ | 1466 / 36 | 2753 / 31 | 293 / 6.5 ¹ |
| Gemma 4 E4B Q4_0 | 96 / 16 | 1433 / 32 | 4128 / 34 | 382 / 2.5 ¹ |
| Qwen3.5 9B Q4_K_M | 54 / 9.5 | 921 / 20 | 1967 / 17 | ✗ ² |
| gpt-oss 20B MXFP4 (MoE) | 88 / 19 | 974 / 37 | ✗ ⁴ | ✗ ⁴ |

¹ 256 prompt tokens and 64 generated tokens, the NPU's fixed prefill chunk. Needs the OpenVINO NPU compiler link from openvino 2026.4.1-2.
² The NPU path only takes Q4_0 models.
³ 128 prompt tokens and 32 generated tokens, from the thread scaling test.
⁴ The OpenVINO backend does not support MXFP4.

## 🧠 OpenVINO GenAI

256 generated tokens, mean of 3 runs after a warm-up. Load includes the first NPU compile; later loads come from the cache.

| Model | GPU tok/s (first token) | NPU tok/s (first token, load) | CPU tok/s (first token) |
| --- | ---: | ---: | ---: |
| Phi-3.5 mini INT4-CW | 53.8 (22 ms) | 39.0 (586 ms, 1.5 s) | 36.0 (60 ms) |
| Qwen3 8B INT4-CW | 26.4 (46 ms) | 23.1 (924 ms, 24 s) | 17.8 (150 ms) |
| Qwen3.5 4B INT4 (VLM pipeline) | 40.5 (37 ms) | ✗ ⁵ | 20.5 (839 ms) |
| Gemma 4 E4B INT4 (VLM pipeline) | 33.4 (90 ms) ⁶ | ✗ ⁵ | 21.9 (126 ms) ⁶ |
| Qwen3.5 9B INT4 (VLM pipeline) | 23.3 (56 ms) | ✗ ⁵ | 12.8 (1184 ms) |

⁵ The NPU compile did not finish in 15 to 50 minutes. Qwen3.5 and Gemma 4 ship as vision-language models without channel-wise (`-cw`) NPU variants.
⁶ Needs openvino 2026.4.1-3; earlier builds abort, see "Problems found". The PyPI wheels, run back to back with the same script, give the same speed: 33.3 tokens/s on the GPU, 21.9 on the CPU.

## 🎙️ whisper.cpp

`whisper-cli`, 66 s of English speech (the JFK sample six times), 8 threads, beam search 5. Every run gave the correct transcript.

| Model | CPU | Vulkan (Arc B390) |
| --- | ---: | ---: |
| large-v3-turbo q5_0 | 29.5 s | 7.8 s |
| large-v3-turbo | 44.7 s | 6.9 s |
| base.en | 3.4 s | 2.6 s |

## 🦙 Ollama against llama.cpp

Ollama 0.40.1 from this repository runs models through its own build of llama.cpp b11351 (with Ollama's compat patches), so the same GGUF file was loaded into Ollama (`FROM <file>.gguf`) and into llama-cpp b11460's `llama-server`, both on Vulkan with every layer on the GPU. Same requests to both: a 628 to 645 token prompt and 128 generated tokens, greedy, mean of 3 runs after a warm-up, a different first line each run so no prompt is reused. Tokens/s.

| Model | llama.cpp prompt / generate | Ollama prompt / generate |
| --- | ---: | ---: |
| Llama 3.2 1B Q4_0 | 3908 / 117.9 | 4192 / 118.3 |
| Qwen3.5 4B Q4_K_M | 692 / 32.5 | 692 / 33.7 |
| Qwen3.5 4B Q4_0 | 697 / 32.5 | 864 / 34.4 |
| Gemma 4 E4B Q4_0 ⁷ | 933 / 30.0 | 936 / 30.4 |
| Qwen3.5 9B Q4_K_M | 499 / 18.5 | 492 / 19.3 |
| gpt-oss 20B MXFP4 (MoE) | 653 / 35.1 | 528 / 35.4 |

⁷ Gemma 4 can end its answer early on a raw prompt, so llama.cpp ran with `ignore_eos` and Ollama with the model's chat template; both generated all 128 tokens.

Ollama is as fast as llama.cpp: generation is within 4 % on every model, and prompt reading is the same except gpt-oss (19 % slower in Ollama) and Qwen3.5 4B Q4_0 (24 % faster). Ollama found the Arc B390 on its own (`OLLAMA_IGPU_ENABLE=1` in the packaged service) and picked a 32768 token context. The numbers are lower than the `llama-bench` table above because a server request includes sampling and runs the prompt as one request rather than a tuned batch.

## 🔎 Embeddings: embeddinggemma-2

Google's Gemma 4 based multimodal embedding model (`embedding_gemma2`, 768 dimensions), Q8_0 GGUF through `llama-server --embeddings`. Six test sentences, two related pairs (camera, NPU) and unrelated ones.

| Device | Speed | Related pairs | Unrelated pairs |
| --- | ---: | ---: | ---: |
| CPU | 36 sentences/s | 0.88, 0.83 | 0.55 to 0.62 |
| Vulkan | 138 sentences/s | 0.88, 0.83 | 0.55 to 0.62 |
| OpenVINO GPU | 106 sentences/s | 0.84, 0.83 | 0.71 to 0.87 ✗ |

CPU and Vulkan agree exactly. The OpenVINO backend's results are wrong: unrelated pairs score as high as related ones, matching the backend's documented limited embedding support.

## 🐞 Problems found

| | Problem | Status |
| --- | --- | --- |
| 🔧 | **NPU compiler not found with the RPMs**: the OpenVINO NPU plugin opens `libopenvino_intel_npu_compiler.so` from its own directory, so every NPU compile through the system OpenVINO failed with "Failed to load compiler library". | Fixed in openvino 2026.4.1-2 (PR #10) |
| 🔧 | **Fedora's python3-torchvision 0.27.1-6 is broken** with torch 2.12: it registers none of its operators, and while it is installed every `transformers` model import fails, which stops `optimum-cli export`. | Left out of the install docs and the optimum-intel suggestion (PR #11); report to Fedora |
| 🔧 | **Fedora's whisper-cpp bundles libggml** and conflicts with llama-cpp. | whisper-cpp 1.9.5 on the shared ggml (PR #12) |
| 🔧 | **Gemma 4 in OpenVINO GenAI aborts** with `_GLIBCXX_ASSERTIONS`: an out of bounds index in `ov::ITensor::copy_to`, called from GenAI's `ModelRunner::forward`. The PyPI build has no assertions and runs it. Upstream as [openvino#38246](https://github.com/openvinotoolkit/openvino/issues/38246). | Fixed in openvino 2026.4.1-3 with the upstream fix from [openvino#38670](https://github.com/openvinotoolkit/openvino/pull/38670) |
| 🐛 | **llama.cpp OpenVINO backend**: wrong embeddings for embeddinggemma-2, no MXFP4, and whisper decoding fails on a `Slice` node ("Axis 3 out of the tensor rank range"). | Report upstream |
| 🐛 | **NPU compile of Qwen3.5 and Gemma 4** (OpenVINO GenAI) never finishes. | Report upstream to OpenVINO |
| 📝 | `llama-bench` with the OpenVINO backend needs `-fa 1`, and the device comes from `GGML_OPENVINO_DEVICE`, not `-dev`. | Documented here |
| 📝 | llama.cpp's default thread count is slow on this CPU (4 P-cores, 8 E-cores, 4 LP E-cores): Qwen3.5 4B generates 12.5 tokens/s by default and 22.9 with `-t 8`. | Use `-t 8` for generation |
| 📝 | `embeddinggemma-2` needs transformers 5.19, but optimum-intel 2.2 caps transformers below 5.6, so it cannot be converted to OpenVINO IR yet. | Waiting for optimum-intel |
| 📝 | The llama-cpp package has no `llama-embedding` (an example program); `llama-server --embeddings` works. | Could enable in the spec |

## 🔁 Reproducing

The scripts are small: `llama-bench` and `whisper-cli` commands as in the tables, and an OpenVINO GenAI loop around `LLMPipeline` or `VLMPipeline` with `GenerationConfig(max_new_tokens=256, ignore_eos=True)` that reads `perf_metrics`. Models:

- GGUF: `ggml-org/gemma-4-E4B-it-GGUF`, `unsloth/Qwen3.5-4B-GGUF`, `unsloth/Qwen3.5-9B-GGUF`, `bartowski/Llama-3.2-1B-Instruct-GGUF`, `ggml-org/gpt-oss-20b-GGUF`, `ggml-org/embeddinggemma-2-GGUF`
- OpenVINO: `OpenVINO/Phi-3.5-mini-instruct-int4-cw-ov`, `OpenVINO/Qwen3-8B-int4-cw-ov`, `OpenVINO/Qwen3.5-4B-int4-ov`, `OpenVINO/gemma-4-E4B-it-int4-ov`, `OpenVINO/Qwen3.5-9B-int4-ov`
- Whisper: `ggerganov/whisper.cpp` (`ggml-large-v3-turbo-q5_0.bin`, `ggml-large-v3-turbo.bin`, `ggml-base.en.bin`)
