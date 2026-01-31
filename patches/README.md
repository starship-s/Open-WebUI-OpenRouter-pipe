# Fork Patches

This directory contains patches for maintaining a fork that stays in sync with upstream while adding custom functionality.

**Fork URL:** https://github.com/starship-s/Open-WebUI-OpenRouter-pipe

## Automatic Updates from This Fork

To install this fork (with all ZDR customizations) directly into Open WebUI:

### Latest Release (Stable)

```
https://github.com/starship-s/Open-WebUI-OpenRouter-pipe/releases/latest/download/open_webui_openrouter_pipe_bundled.py
```

### Development Branch (Bleeding Edge)

```
https://github.com/starship-s/Open-WebUI-OpenRouter-pipe/releases/download/dev/open_webui_openrouter_pipe_bundled.py
```

### Installation Steps

1. In Open WebUI: **Admin Panel** → **Functions** → **+** → **Import from Link**
2. Paste the URL above
3. Toggle the pipe **ON**
4. Click the **⚙️ gear icon** → paste your OpenRouter API key → **Save**

This will install the fork version which includes:
- ZDR (Zero Data Retention) enforcement filter
- `HIDE_MODELS_WITHOUT_ZDR` valve to hide non-ZDR models
- `TASK_TITLE_MODEL_ID` and `TASK_FOLLOWUP_MODEL_ID` for task model overrides
- `MODEL_ICON_OVERRIDES` for custom model icons

### Creating Releases on This Fork

The GitHub Actions workflow (`bundle.yml`) automatically creates releases:

**For stable releases:**
```bash
# After committing your changes
git tag v2.0.4  # Use semantic versioning
git push origin v2.0.4
```
This creates a versioned release at `releases/latest/download/open_webui_openrouter_pipe_bundled.py`

**For development builds:**
```bash
git push origin dev
```
This creates/updates the pre-release at `releases/download/dev/open_webui_openrouter_pipe_bundled.py`

## Strategy for Staying in Sync with Upstream

### Initial Setup

```bash
# Add upstream remote (one-time) - points to the original repo for syncing
git remote add upstream https://github.com/rbb-dev/Open-WebUI-OpenRouter-pipe.git

# This fork is at:
# https://github.com/starship-s/Open-WebUI-OpenRouter-pipe

# Verify remotes
git remote -v
```

### Syncing with Upstream

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream into this fork (from main branch)
git checkout main
git merge upstream/main

# Or rebase your changes on top of upstream
git rebase upstream/main
```

### Managing Custom Files

The ZDR filter (`filters/openrouter_zdr_filter.py`) is a **new file** that doesn't exist in upstream. This makes syncing easy:

1. Upstream changes won't conflict with your custom filter
2. Just merge/rebase normally - your filter stays intact
3. If upstream adds a file with the same name, you'll get a conflict to resolve manually

**Note:** The pipe modifications (0002 patch) modify existing upstream files. When upstream updates these files, you may need to resolve merge conflicts. The changes are localized and well-documented to make this easier.

## Patches in This Directory

### 0001-add-zdr-filter.patch

Adds the ZDR (Zero Data Retention) filter that enforces `provider.zdr=true` on all OpenRouter requests.

- **Type:** New file (no merge conflicts expected)
- **Files added:** `filters/openrouter_zdr_filter.py`

### 0002-add-zdr-model-hiding.patch

Adds the `HIDE_MODELS_WITHOUT_ZDR` valve to the pipe, which hides models that don't have ZDR-compliant providers.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/core/config.py` - Adds valve and constant
  - `open_webui_openrouter_pipe/models/registry.py` - Adds ZDR endpoint fetching
  - `open_webui_openrouter_pipe/pipe.py` - Adds ZDR filtering to model list

### 0003-add-task-model-overrides.patch

Adds valves to override which models are used for Open WebUI background tasks (title generation, follow-up suggestions).

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/core/config.py` - Adds `TASK_TITLE_MODEL_ID` and `TASK_FOLLOWUP_MODEL_ID` valves
  - `open_webui_openrouter_pipe/requests/task_model_adapter.py` - Applies model overrides

## Task Model Override Feature

| Valve | Purpose |
|-------|---------|
| `TASK_TITLE_MODEL_ID` | Force a specific model for chat title generation |
| `TASK_FOLLOWUP_MODEL_ID` | Force a specific model for follow-up question suggestions |

**Use case:** Use cheaper/faster models (e.g., `google/gemini-flash-1.5`) for background tasks while keeping more capable models for main chat interactions.

**Configuration:**
1. Go to **Admin → Functions → [OpenRouter Pipe] → Valves**
2. Set `TASK_TITLE_MODEL_ID` to your preferred model (e.g., `google/gemini-flash-1.5`)
3. Set `TASK_FOLLOWUP_MODEL_ID` to your preferred model (can be the same or different)

Leave blank to use the default behavior (same model as the chat).

### 0004-add-model-icon-overrides.patch

Adds the `MODEL_ICON_OVERRIDES` valve to customize model icons via JSON configuration.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/core/config.py` - Adds `MODEL_ICON_OVERRIDES` valve
  - `open_webui_openrouter_pipe/models/catalog_manager.py` - Parses and applies icon overrides

## Model Icon Override Feature

| Valve | Purpose |
|-------|---------|
| `MODEL_ICON_OVERRIDES` | JSON object mapping authors or model IDs to custom icon URLs |

**Matching priority:**
1. Full model slug (e.g., `"openai/gpt-4o"`) - highest priority
2. Author prefix (e.g., `"openai"`) - matches all models from that author

**Example configuration:**

```json
{
    "01-ai": "https://example.com/01ai.png",
    "ai21": "https://example.com/ai21.png",
    "anthropic/claude-3-opus": "https://example.com/opus.png"
}
```

This will:
- Use the custom icon for all `01-ai/*` models
- Use the custom icon for all `ai21/*` models
- Use the opus icon specifically for `anthropic/claude-3-opus` (other anthropic models unaffected)

**Configuration:**
1. Go to **Admin → Functions → [OpenRouter Pipe] → Valves**
2. Set `MODEL_ICON_OVERRIDES` to your JSON configuration
3. Refresh the model list

### 0005-add-zdr-auto-install.patch

Adds ZDR filter auto-install, per-model attachment, and default-on behavior.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/core/config.py` - Adds `AUTO_INSTALL_ZDR_FILTER`, `AUTO_ATTACH_ZDR_FILTER`, and `AUTO_DEFAULT_ZDR_FILTER` valves
  - `open_webui_openrouter_pipe/pipe.py` - Adds filter render method, ensure method, and auto-install logic
  - `open_webui_openrouter_pipe/models/catalog_manager.py` - Adds per-model ZDR filter attachment

| Valve | Default | Description |
|-------|---------|-------------|
| `AUTO_INSTALL_ZDR_FILTER` | True | Automatically creates/updates the ZDR filter function |
| `AUTO_ATTACH_ZDR_FILTER` | True | Attaches ZDR filter to models with ZDR-compliant providers |
| `AUTO_DEFAULT_ZDR_FILTER` | True | Enables ZDR by default on attached models |

**How it works:**
- `AUTO_INSTALL_ZDR_FILTER`: Creates the ZDR filter function in Open WebUI on first load
- `AUTO_ATTACH_ZDR_FILTER`: For each model with ZDR providers, adds the filter to its `filterIds` (making the toggle appear in Integrations)
- `AUTO_DEFAULT_ZDR_FILTER`: For attached models, adds the filter to `defaultFilterIds` (enabling ZDR by default)
- Users can still toggle ZDR off per chat in **Settings → Integrations**

**Per-model control:** Operators can disable auto-attachment on specific models via model params:
- `disable_zdr_auto_attach`: Prevents filter attachment
- `disable_zdr_default_on`: Prevents default-on behavior

### 0006-fix-zdr-slug-matching.patch

Fixes ZDR endpoint matching when `/endpoints/zdr` only provides label-based names
(`"Provider | author/model"`) and omits structured slug fields.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/models/registry.py` - Improves slug extraction + alias mapping

**Key changes:**
- Extracts slugs from label strings in ZDR endpoint entries
- Adds alias mapping using `endpoint.name` and nested `endpoint.model` fields
- Falls back to base ids for variants (e.g., `:free`)
  - Ensures ZDR provider lookups succeed for model variants

### 0007-add-zdr-filter-icon-and-provider-exclusions.patch

Adds a shield icon to the ZDR filter toggle UI and introduces the
`ZDR_EXCLUDED_PROVIDERS` valve to exclude specific providers from ZDR routing.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `filters/openrouter_zdr_filter.py` - Adds a shield icon to the toggle UI
  - `open_webui_openrouter_pipe/pipe.py` - Updates embedded ZDR filter source
  - `open_webui_openrouter_pipe/core/config.py` - Adds `ZDR_EXCLUDED_PROVIDERS`
  - `open_webui_openrouter_pipe/models/registry.py` - Filters ZDR providers by exclusions
  - `open_webui_openrouter_pipe/models/catalog_manager.py` - Uses exclusions for attach/default
  - `open_webui_openrouter_pipe/requests/orchestrator.py` - Applies provider.ignore
  - `docs/valves_and_configuration_atlas.md` - Documents the new valve

**Key changes:**
- Adds a shield icon (data URI) to the ZDR filter toggle UI
- Adds `ZDR_EXCLUDED_PROVIDERS` (CSV of provider slugs)
- Excludes those providers from ZDR model matching and auto-attach
- Applies `provider.ignore` when ZDR is active

### 0008-add-data-collection-deny-valve.patch

Adds a global valve to force `provider.data_collection="deny"` on every
OpenRouter request.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/core/config.py` - Adds `ENFORCE_DATA_COLLECTION_DENY`
  - `open_webui_openrouter_pipe/requests/orchestrator.py` - Applies provider override
  - `docs/valves_and_configuration_atlas.md` - Documents the valve
  - `README.md` - Lists the valve in fork features
  - `open_webui_openrouter_pipe.py` - Bumps version metadata

**Key changes:**
- Adds `ENFORCE_DATA_COLLECTION_DENY` (default: on)
- Forces `provider.data_collection="deny"` for every request

### 0009-fix-zdr-excluded-providers-helper.patch

Fixes the placement of the ZDR excluded providers helper so it is available on
the Pipe class for model filtering, catalog sync, and request handling.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/pipe.py` - Adds missing Pipe helper methods

**Key changes:**
- Adds Pipe CSV parsing helper for ZDR exclusions
- Adds Pipe helpers for excluded providers and provider.ignore merges

### 0010-sync-fork-metadata-and-tests.patch

Keeps fork metadata, documentation, and tests aligned with the ZDR feature set
while rebasing onto upstream updates.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `README.md` - Updates Open WebUI compatibility badge
  - `open_webui_openrouter_pipe.py` - Keeps required version + fork version
  - `open_webui_openrouter_pipe/__init__.py` - Updates `__version__` fallback
  - `pyproject.toml` - Updates project version
  - `CHANGELOG.md` - Keeps fork release headings
  - `filters/README.md` - Documents ZDR filter v0.4.0 behavior
  - `tests/test_models.py` - Adds ZDR auto-install valves to sync key tests

**Key changes:**
- Maintains `required_open_webui_version: 0.7.0`
- Keeps fork version strings at `2.0.6-zdr`
- Ensures ZDR auto-install valves are tracked in catalog sync tests

### 0011-fix-thinking-output-duplication.patch

Prevents duplicated thinking output when reasoning arrives both incrementally
and as a snapshot, and avoids double status emission in "both" thinking mode.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/streaming/streaming_core.py` - Skips redundant reasoning snapshots and tags status emission
  - `open_webui_openrouter_pipe/streaming/event_emitter.py` - Skips duplicate status emission when tagged
  - `tests/test_streaming_handler.py` - Adds reasoning dedupe coverage
  - `tests/test_event_emitter.py` - Adds status emission dedupe coverage

### 0012-dedupe-status-events.patch

Deduplicates consecutive identical status messages to prevent repeated UI
status lines.

- **Type:** Modifies existing files (may require conflict resolution on upstream updates)
- **Files modified:**
  - `open_webui_openrouter_pipe/streaming/event_emitter.py` - Skips consecutive identical status events
  - `tests/test_event_emitter.py` - Adds status dedupe coverage

## ZDR Feature Summary

The ZDR feature has two components:

| Component | Purpose | Location |
|-----------|---------|----------|
| **ZDR Filter** | Enforces `provider.zdr=true` on all requests | `filters/openrouter_zdr_filter.py` |
| **HIDE_MODELS_WITHOUT_ZDR** | Hides models without ZDR providers from the model list | Pipe valve (in Admin → Functions → Valves) |
| **ZDR_EXCLUDED_PROVIDERS** | Excludes provider slugs while ZDR is enabled | Pipe valve (in Admin → Functions → Valves) |

**Recommended setup for maximum ZDR compliance:**
1. Install the ZDR filter and enable it globally
2. Enable `HIDE_MODELS_WITHOUT_ZDR` in the pipe valves
3. Optionally set `ZDR_EXCLUDED_PROVIDERS` to skip specific providers

## Installing the ZDR Filter in Open WebUI

### Option 1: Automatic (Recommended - Fork Only)

**If you installed the fork's bundled pipe** (from the release URL at the top), the ZDR filter is automatically installed!

- The filter appears in **Admin → Functions** as "ZDR (Zero Data Retention)"
- Toggle it on/off per chat in **Settings → Integrations**
- It's kept up-to-date automatically with the pipe
- No manual installation needed

This is controlled by the `AUTO_INSTALL_ZDR_FILTER` valve (enabled by default).

### Option 2: Manual Installation (Upstream or Manual Install)

If you're using the upstream pipe or want to manually install the filter:

1. Copy the contents of `filters/openrouter_zdr_filter.py`
2. In Open WebUI, go to **Admin → Functions → Add Function**
3. Paste the filter code and save
4. Enable the filter globally or per-model

### Option 3: Import from URL (Upstream or Manual Install)

```
https://raw.githubusercontent.com/starship-s/Open-WebUI-OpenRouter-pipe/main/filters/openrouter_zdr_filter.py
```

1. In Open WebUI, go to **Admin → Functions → Add Function → Import from URL**
2. Paste the URL above
3. Save and enable

## Enabling HIDE_MODELS_WITHOUT_ZDR

1. Go to **Admin → Functions → [OpenRouter Pipe] → Valves**
2. Find **HIDE_MODELS_WITHOUT_ZDR** and set it to `True`
3. Refresh the model list

This will hide any model that doesn't have a ZDR-compliant endpoint entry in OpenRouter's `/endpoints/zdr` catalog.

## Notes

- The ZDR filter is toggleable - users can disable it per-chat if needed
- Not all providers support ZDR; requests may fail if no ZDR-compliant providers are available for a model
- When `HIDE_MODELS_WITHOUT_ZDR` is enabled, only models with at least one ZDR provider will appear
- Consider enabling `ALLOW_FALLBACKS` in provider routing if you want fallback behavior
