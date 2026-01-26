# filters/

This folder contains reference Open WebUI filter functions used alongside the OpenRouter pipe.

**Fork URL:** https://github.com/starship-s/Open-WebUI-OpenRouter-pipe

## ZDR (Zero Data Retention) filter

- `openrouter_zdr_filter.py` enforces Zero Data Retention mode on all OpenRouter requests.
- **New in v0.4.0**: The filter now automatically fetches ZDR-compliant providers from OpenRouter's `/endpoints/zdr` endpoint and sets `provider.only` with the list of compliant providers for each model.
- Provider lists are cached for 1 hour to minimize API calls.
- The filter sets both `provider.zdr=true` and `provider.only=[...]` to ensure only ZDR-compliant providers handle your requests.
- The filter is toggleable — users can disable it per-chat if needed.
- **Requirements**: The filter requires `aiohttp` and the `OPENROUTER_API_KEY` environment variable to be set.

To install: Copy the contents into Open WebUI Functions (Admin → Functions → Add Function).

### How It Works

When enabled, for each request the filter will:
1. Extract the model ID from the request
2. Query the cached ZDR endpoint data (or fetch it if cache is stale)
3. Look up which providers support ZDR for that specific model
4. Set `provider.only` to the list of ZDR-compliant providers
5. Set `provider.zdr=true` for additional enforcement

This ensures that OpenRouter will **only route to providers that support Zero Data Retention** for the requested model.

### Hiding Non-ZDR Models

To also **hide** models that don't have ZDR providers from the model list, enable the `HIDE_MODELS_WITHOUT_ZDR` valve on the pipe itself:
1. Go to **Admin → Functions → [OpenRouter Pipe] → Valves**
2. Set `HIDE_MODELS_WITHOUT_ZDR` to `True`
3. Refresh the model list

To **exclude specific providers** while ZDR is enabled, set `ZDR_EXCLUDED_PROVIDERS` to a comma-separated list (e.g., `amazon-bedrock, novita/fp8`).

## OpenRouter Search toggle

- `openrouter_search_toggle.py` is the companion *toggleable filter* used to enable OpenRouter-native web search.
- The pipe embeds a canonical copy of this filter and can **auto-install/auto-update** it into Open WebUI’s Functions DB when `AUTO_INSTALL_ORS_FILTER` is enabled.
- The filter is included here for review and manual installation, but **the live behavior is driven by the embedded copy inside the pipe** when auto-install is enabled.

If you edit `openrouter_search_toggle.py` in this repo, it will not automatically update your running Open WebUI unless you paste/install it manually (or you update the embedded filter source in the pipe).

## Direct Uploads toggle

- `openrouter_direct_uploads_toggle.py` is the companion *toggleable filter* used to bypass Open WebUI RAG for chat uploads and forward them to OpenRouter as direct file/audio/video inputs.
- The pipe embeds a canonical copy of this filter and can **auto-install/auto-update** it into Open WebUI’s Functions DB when `AUTO_INSTALL_DIRECT_UPLOADS_FILTER` is enabled.
- The filter is included here for review and manual installation, but **the live behavior is driven by the embedded copy inside the pipe** when auto-install is enabled.

If you edit `openrouter_direct_uploads_toggle.py` in this repo, it will not automatically update your running Open WebUI unless you paste/install it manually (or you update the embedded filter source in the pipe).

Reference documentation:
- [OpenRouter Direct Uploads (bypass OWUI RAG)](../docs/openrouter_direct_uploads.md)
