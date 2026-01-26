# Open WebUI → OpenRouter Pipe

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.10--zdr-blue.svg)](https://github.com/starship-s/Open-WebUI-OpenRouter-pipe)
[![Open WebUI Compatible](https://img.shields.io/badge/Open%20WebUI-0.6.28%2B-green.svg)](https://openwebui.com/)
[![Fork](https://img.shields.io/badge/fork-starship--s-purple.svg)](https://github.com/starship-s/Open-WebUI-OpenRouter-pipe)

> **This is a fork** of [rbb-dev/Open-WebUI-OpenRouter-pipe](https://github.com/rbb-dev/Open-WebUI-OpenRouter-pipe) with ZDR (Zero Data Retention) enforcement and additional personal customizations.

**Access 350+ AI models through one interface.**

Use GPT-5.2, Gemini 3, Claude Opus, Llama 4, and hundreds more — all from your Open WebUI, all through OpenRouter's unified API.

![output](https://github.com/user-attachments/assets/c937443b-f1be-4091-9555-b49789f16a97)

---

## What this is (in one minute)

* **OpenRouter Integration Subsystem for Open WebUI**: this isn't a standalone service. Open WebUI loads it as a Function / Pipe.
* **Multimodal-aware routing adapters**: it inspects the payload (text + images/files/audio/video) and selects the appropriate endpoint + format the target model actually supports.
* **Responses-first endpoint routing**: it builds canonical requests and routes to `/responses` or `/chat/completions` depending on model rules, fallback behaviour, or attachments.
* **Operator controls via valves**: routing, limits, storage, security posture, telemetry, and templates.

**If you fork this:** it’s worth keeping the tests and running them for changes (`pytest`) — and running `pyright` as well.  
It keeps behaviour consistent and makes debugging a lot quicker.

For the full documentation, start with `docs/README.md`.
If you're reviewing code, start with the pytest test suite in `tests/`, 3200+ pytest tests with broad coverage.


Check GitHub CI test workflows.

---


## What You Get

🎯 **Every Model, One Place**
GPT-5.2, Gemini 3, Claude Opus, Llama 4, DeepSeek, Qwen, Command R+ — browse them all, try them all, compare them all. One API key, one bill. Plus model variants (`:free`, `:thinking`, `:exacto`) for specialized routing.

🖼️ **Multimodal That Actually Works**
Drop in images, PDFs, documents. The pipe figures out what each model supports and handles the rest.

🔧 **Tools & Web Search**
Your Open WebUI tools work seamlessly. OpenRouter's native web search is one toggle away.

🎨 **Complete Integration**
Model icons and descriptions sync automatically. Capabilities show up in the UI. It feels native because it is.

💬 **Clear Communication**
Helpful error messages, real-time status updates, and transparent cost tracking per request.

---

## For IT & Operations

⚡ **Production Hardened**
Rate limiting, circuit breakers, request admission controls, and graceful degradation — built for real workloads, not demos.

🔐 **Security First**
Encrypted credential storage, SSRF protection with HTTPS-only remote fetches by default (HTTP allowlist available), no secrets in logs. Designed for environments where security reviews happen.

📊 **Cost & Attribution**
Track spending per user, per session. Optional Redis export for billing integration. Know who's using what.

📝 **Audit Trail**
Optional encrypted session logs for incident response. Request identifiers flow through to OpenRouter for end-to-end attribution.

🛡️ **Enterprise Controls**
Encryption, retention policies, request attribution, and operational hooks your governance program can build on.

---

## Quick Start

**1. Install**

In Open WebUI: **Admin Panel** → **Functions** → **+** → **Import from Link**

```
https://github.com/starship-s/Open-WebUI-OpenRouter-pipe/releases/latest/download/open_webui_openrouter_pipe_bundled.py
```

This downloads the latest stable release — a single-file bundle automatically generated from the modular source code on every release.

<details>
<summary>Alternative: bleeding-edge from dev branch</summary>

For the latest development commits (may be unstable):

```
https://github.com/starship-s/Open-WebUI-OpenRouter-pipe/releases/download/dev/open_webui_openrouter_pipe_bundled.py
```

</details>

### Fork-Specific Features

This fork includes additional features not in upstream:

- **ZDR Filter** - Enforces Zero Data Retention on all requests
  - `AUTO_INSTALL_ZDR_FILTER` - Auto-installs the filter (default: on)
  - `AUTO_ATTACH_ZDR_FILTER` - Attaches filter to models with ZDR providers (default: on)
  - `AUTO_DEFAULT_ZDR_FILTER` - Enables ZDR by default on supported models (default: on)
- **`HIDE_MODELS_WITHOUT_ZDR`** valve - Hides models without ZDR-compliant providers
- **`TASK_TITLE_MODEL_ID`** / **`TASK_FOLLOWUP_MODEL_ID`** valves - Override models for background tasks
- **`MODEL_ICON_OVERRIDES`** valve - Custom model icons via JSON configuration

See `patches/README.md` for details.

**2. Enable**

Toggle the pipe **ON** (the switch next to the function name).

**3. Add Your API Key**

Click the **⚙️ gear icon** on the pipe → paste your [OpenRouter API key](https://openrouter.ai/keys) → **Save**.

**4. Select a Model**

Back in the chat, click the model dropdown — you'll see all OpenRouter models. Pick one.

**5. Chat!**

That's it. Start talking.

---

## Requirements

- Open WebUI 0.6.28+
- An [OpenRouter](https://openrouter.ai/) account
- `WEBUI_SECRET_KEY` configured (required for encrypted credential storage)

---

## Documentation

Everything else lives in [`docs/`](docs/README.md):

- [Configuration Reference](docs/valves_and_configuration_atlas.md) — all the knobs and switches
- [Model Variants & Presets](docs/model_variants_and_presets.md) — using :free, :thinking, :exacto variants and OpenRouter presets
- [Security Guide](docs/security_and_encryption.md) — production hardening
- [Tool Integration](docs/tooling_and_integrations.md) — extending with tools
- [Cost & Attribution](docs/openrouter_integrations_and_telemetry.md) — billing and tracking
- [Troubleshooting](docs/error_handling_and_user_experience.md) — when things go sideways

---

## License

MIT — use it, fork it, ship it.
