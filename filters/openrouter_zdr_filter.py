"""
title: ZDR (Zero Data Retention)
author: starship-s
author_url: https://github.com/starship-s/Open-WebUI-OpenRouter-pipe
id: openrouter_zdr_filter
description: Enforces Zero Data Retention mode on all OpenRouter requests. Only ZDR-compliant providers will be used.
version: 0.4.0
license: MIT
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from typing import Any, Dict

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from open_webui.env import SRC_LOG_LEVELS
except ImportError:
    SRC_LOG_LEVELS = {}

OWUI_OPENROUTER_PIPE_MARKER = "openrouter_pipe:zdr_filter:v1"
_FEATURE_FLAG = "zdr"
_OPENROUTER_TITLE = "Open WebUI OpenRouter ZDR Filter"
_OPENROUTER_REFERER = "https://github.com/starship-s/Open-WebUI-OpenRouter-pipe"
_OPENROUTER_FRONTEND_MODELS_URL = "https://openrouter.ai/api/frontend/models"
_OPENROUTER_ZDR_ENDPOINT_SUFFIX = "/endpoints/zdr"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_ZDR_CACHE_SECONDS = 3600  # Cache for 1 hour


class ZDRProviderCache:
    """Caches ZDR provider mappings from OpenRouter."""
    
    _providers: Dict[str, list[str]] = {}  # normalized model_id -> provider tags
    _last_fetch: float = 0.0
    _lock: asyncio.Lock = asyncio.Lock()
    
    @classmethod
    async def get_providers_for_model(
        cls,
        model_id: str,
        *,
        api_key: str,
        base_url: str = _OPENROUTER_BASE_URL,
        http_referer: str | None = None,
        logger: logging.Logger,
    ) -> list[str]:
        """Get ZDR providers for a model, fetching and caching if needed."""
        if not model_id:
            return []
        
        # Check if cache is still valid
        now = time.time()
        if cls._providers and (now - cls._last_fetch) < _ZDR_CACHE_SECONDS:
            return cls._get_cached_providers(model_id)
        
        # Refresh cache
        async with cls._lock:
            # Double-check after acquiring lock
            if cls._providers and (now - cls._last_fetch) < _ZDR_CACHE_SECONDS:
                return cls._get_cached_providers(model_id)
            
            await cls._refresh_cache(
                api_key=api_key,
                base_url=base_url,
                http_referer=http_referer,
                logger=logger,
            )
            return cls._get_cached_providers(model_id)
    
    @classmethod
    def _get_cached_providers(cls, model_id: str) -> list[str]:
        """Get providers from cache for a normalized model ID."""
        normalized = cls._normalize_model_id(model_id)
        providers = cls._providers.get(normalized, [])
        
        # If not found, try without variant suffix (e.g., :free)
        if not providers and ":" in normalized:
            base = normalized.split(":", 1)[0]
            providers = cls._providers.get(base, [])
        
        return list(providers)
    
    @classmethod
    async def _refresh_cache(
        cls,
        *,
        api_key: str,
        base_url: str,
        http_referer: str | None,
        logger: logging.Logger,
    ) -> None:
        """Fetch ZDR endpoints from OpenRouter and rebuild the cache."""
        if not aiohttp:
            logger.warning("aiohttp not available, cannot fetch ZDR endpoints")
            return
        
        url = base_url.rstrip("/") + _OPENROUTER_ZDR_ENDPOINT_SUFFIX
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Title": _OPENROUTER_TITLE,
            "HTTP-Referer": (http_referer or _OPENROUTER_REFERER),
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    resp.raise_for_status()
                    payload = await resp.json()
                frontend_data = await cls._fetch_frontend_catalog(session, logger)
        except Exception as exc:
            logger.debug("Failed to fetch ZDR endpoints: %s", exc)
            return
        
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list):
            logger.debug("ZDR endpoints payload had unexpected structure")
            return
        
        # Build alias mapping from frontend catalog for canonical normalization.
        alias_to_norm = cls._build_alias_map(frontend_data)

        # Build mapping: normalized model_id -> [provider tags]
        mapping: Dict[str, list[str]] = {}
        for entry in data:
            if not isinstance(entry, dict):
                continue

            model_slug = cls._normalize_zdr_model_slug(entry)
            if not model_slug:
                continue

            provider_tag = cls._extract_provider_tag(entry)
            if not provider_tag:
                continue

            normalized = cls._base_model(cls._normalize_model_id(model_slug))
            canonical_norm = alias_to_norm.get(normalized, normalized)
            providers = mapping.setdefault(canonical_norm, [])
            if provider_tag not in providers:
                providers.append(provider_tag)
        
        cls._providers = mapping
        cls._last_fetch = time.time()
        logger.debug("Refreshed ZDR provider cache with %d models", len(mapping))
    
    @staticmethod
    async def _fetch_frontend_catalog(
        session: "aiohttp.ClientSession", logger: logging.Logger
    ) -> dict[str, Any] | None:
        """Best-effort fetch of the frontend catalog for alias mapping."""
        try:
            async with session.get(
                _OPENROUTER_FRONTEND_MODELS_URL,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
                payload = await resp.json()
        except Exception as exc:
            logger.debug("OpenRouter frontend catalog fetch failed: %s", exc)
            return None

        if isinstance(payload, dict):
            return payload
        logger.debug(
            "Frontend catalog returned unexpected payload type: %s",
            type(payload).__name__,
        )
        return None

    @staticmethod
    def _normalize_model_id(model_id: str) -> str:
        """Normalize a model ID for cache lookup."""
        if not isinstance(model_id, str):
            return ""

        # Remove openrouter.ai/ prefix if present
        normalized = model_id.strip().lower()
        if normalized.startswith("openrouter.ai/"):
            normalized = normalized[14:]

        # Sanitize special characters
        normalized = re.sub(r"[^a-z0-9/:._-]", "-", normalized)

        return normalized

    @staticmethod
    def _base_model(model_id: str) -> str:
        """Strip variant suffixes like ':free' for base mapping."""
        if not isinstance(model_id, str):
            return ""
        return model_id.split(":", 1)[0]

    @staticmethod
    def _safe_split(value: Any, sep: str) -> list[str]:
        if not isinstance(value, str):
            return []
        return [part.strip() for part in value.split(sep) if part and part.strip()]

    @staticmethod
    def _extract_slug_from_label(value: Any) -> str:
        """Extract an author/model slug from a label like 'Provider | author/model'."""
        if not isinstance(value, str):
            return ""
        candidate = value.strip()
        if not candidate:
            return ""

        parts = ZDRProviderCache._safe_split(candidate, "|")
        if parts:
            candidate = parts[-1]

        match = re.search(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.:-]+)", candidate)
        if match:
            return match.group(1)

        if "/" in candidate:
            return candidate.strip()
        return ""

    @staticmethod
    def _normalize_zdr_model_slug(value: Any) -> str:
        """Extract the model slug from a ZDR endpoint record."""

        def _add_candidate(val: Any, *, split_name: bool, sink: list[str]) -> None:
            if isinstance(val, str):
                candidate = val.strip()
                if not candidate:
                    return
                if split_name:
                    slug = ZDRProviderCache._extract_slug_from_label(candidate)
                    if slug:
                        sink.append(slug)
                sink.append(candidate)
                return

            if isinstance(val, dict):
                for key in (
                    "id",
                    "slug",
                    "model",
                    "model_slug",
                    "model_variant_slug",
                    "model_variant_permaslug",
                    "name",
                ):
                    _add_candidate(val.get(key), split_name=(key == "name"), sink=sink)

        candidates: list[str] = []
        if isinstance(value, dict):
            for key in ("model", "model_slug", "model_id", "slug", "id"):
                _add_candidate(value.get(key), split_name=False, sink=candidates)

            endpoint = value.get("endpoint")
            if isinstance(endpoint, dict):
                for key in (
                    "model",
                    "model_slug",
                    "model_variant_slug",
                    "model_variant_permaslug",
                    "slug",
                    "permaslug",
                    "id",
                    "name",
                ):
                    _add_candidate(
                        endpoint.get(key), split_name=(key == "name"), sink=candidates
                    )

            _add_candidate(value.get("name"), split_name=True, sink=candidates)
        else:
            _add_candidate(value, split_name=True, sink=candidates)

        for candidate in candidates:
            if candidate:
                return candidate
        return ""

    @staticmethod
    def _build_alias_map(frontend_data: dict[str, Any] | None) -> dict[str, str]:
        """Build alias -> canonical model mapping from frontend catalog."""
        if not isinstance(frontend_data, dict):
            return {}
        raw_items = frontend_data.get("data")
        if not isinstance(raw_items, list):
            return {}

        alias_to_norm: dict[str, str] = {}
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            slug = item.get("slug")
            if not isinstance(slug, str) or not slug:
                continue
            canonical_norm = ZDRProviderCache._base_model(
                ZDRProviderCache._normalize_model_id(slug)
            )
            if not canonical_norm:
                continue

            aliases: set[str] = set()
            for key in ("slug", "permaslug", "canonical_slug"):
                val = item.get(key)
                if isinstance(val, str) and val:
                    aliases.add(val)
            endpoint = item.get("endpoint")
            if isinstance(endpoint, dict):
                for key in (
                    "model",
                    "model_slug",
                    "model_variant_slug",
                    "model_variant_permaslug",
                    "slug",
                    "permaslug",
                ):
                    val = endpoint.get(key)
                    if isinstance(val, str) and val:
                        aliases.add(val)

            for alias in aliases:
                alias_norm = ZDRProviderCache._base_model(
                    ZDRProviderCache._normalize_model_id(alias)
                )
                if alias_norm:
                    alias_to_norm.setdefault(alias_norm, canonical_norm)

        return alias_to_norm

    @staticmethod
    def _extract_provider_tag(entry: dict) -> str:
        """Extract provider tag from a ZDR endpoint entry."""
        tag = entry.get("tag") or entry.get("provider_name")
        if isinstance(tag, str) and tag.strip():
            return tag.strip()

        provider = entry.get("provider")
        if isinstance(provider, dict):
            tag = provider.get("tag") or provider.get("name") or provider.get("id")
            if isinstance(tag, str) and tag.strip():
                return tag.strip()

        endpoint = entry.get("endpoint")
        if isinstance(endpoint, dict):
            provider_info = endpoint.get("provider_info")
            if isinstance(provider_info, dict):
                tag = (
                    provider_info.get("slug")
                    or provider_info.get("displayName")
                    or provider_info.get("tag")
                    or provider_info.get("name")
                )
                if isinstance(tag, str) and tag.strip():
                    return tag.strip()

        return ""


class Filter:
    """
    Zero Data Retention filter for OpenRouter requests.
    
    When enabled, this filter sets provider.zdr=true on all requests,
    ensuring that only ZDR-compliant providers are used. This is useful
    for compliance with data retention policies.
    
    This filter enforces ZDR on requests. To also HIDE non-ZDR models from
    the model list, enable the HIDE_MODELS_WITHOUT_ZDR valve on the pipe itself
    (Admin -> Functions -> [OpenRouter Pipe] -> Valves).

    To exclude specific providers while ZDR is enabled, set the
    ZDR_EXCLUDED_PROVIDERS valve on the pipe (comma-separated provider slugs).
    
    See: https://openrouter.ai/docs/provider-routing
    """
    
    # Toggleable filter (shows a switch in the Integrations menu).
    # Set to True so users can disable ZDR per-chat if needed.
    toggle = True

    def __init__(self) -> None:
        self.log = logging.getLogger("openrouter.zdr.filter")
        self.log.setLevel(SRC_LOG_LEVELS.get("OPENAI", logging.INFO))
        self.toggle = True
        self.icon = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAACXBIWXMAAAsTAAALEwEAmpwYAAAE8GlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgOS4xLWMwMDIgNzkuYTZhNjM5NiwgMjAyNC8wMy8xMi0wNzo0ODoyMyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDI1LjExIChXaW5kb3dzKSIgeG1wOkNyZWF0ZURhdGU9IjIwMjYtMDEtMjZUMDU6MDU6MDItMDc6MDAiIHhtcDpNb2RpZnlEYXRlPSIyMDI2LTAxLTI2VDA1OjA1OjI3LTA3OjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDI2LTAxLTI2VDA1OjA1OjI3LTA3OjAwIiBkYzpmb3JtYXQ9ImltYWdlL3BuZyIgcGhvdG9zaG9wOkNvbG9yTW9kZT0iMyIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDowOTdhYmM1Yi04OTNlLWE0NDQtOWY1Ny1jZWI4YmExM2FkYTAiIHhtcE1NOkRvY3VtZW50SUQ9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"
        )

    def inlet(
        self,
        body: dict[str, Any],
        __metadata__: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Inject ZDR requirement into request metadata for the OpenRouter pipe."""
        if __metadata__ is not None and not isinstance(__metadata__, dict):
            return body

        if isinstance(__metadata__, dict):
            # Get or create the openrouter_pipe metadata section
            prev_pipe_meta = __metadata__.get("openrouter_pipe")
            pipe_meta = dict(prev_pipe_meta) if isinstance(prev_pipe_meta, dict) else {}
            __metadata__["openrouter_pipe"] = pipe_meta

            # Get or create the provider section
            prev_provider = pipe_meta.get("provider")
            provider = dict(prev_provider) if isinstance(prev_provider, dict) else {}
            pipe_meta["provider"] = provider

            # Set ZDR to true
            provider["zdr"] = True
            
            # Get model ID from body
            model_id = body.get("model_id", "") or body.get("model", "")
            if not model_id and isinstance(body.get("models"), list):
                models_list = body["models"]
                if models_list:
                    model_id = models_list[0]
            
            # Fetch ZDR providers for this model
            if model_id and aiohttp:
                api_key = os.environ.get("OPENROUTER_API_KEY", "")
                http_referer = os.environ.get("HTTP_REFERER_OVERRIDE", "").strip() or None
                if api_key:
                    try:
                        # Run async function in sync context
                        loop = None
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # If loop is running, create a new one for this sync context
                                loop = asyncio.new_event_loop()
                                providers = loop.run_until_complete(
                                    ZDRProviderCache.get_providers_for_model(
                                        model_id,
                                        api_key=api_key,
                                        http_referer=http_referer,
                                        logger=self.log,
                                    )
                                )
                                loop.close()
                            else:
                                providers = loop.run_until_complete(
                                    ZDRProviderCache.get_providers_for_model(
                                        model_id,
                                        api_key=api_key,
                                        http_referer=http_referer,
                                        logger=self.log,
                                    )
                                )
                        except RuntimeError:
                            # No event loop, create one
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            providers = loop.run_until_complete(
                                ZDRProviderCache.get_providers_for_model(
                                    model_id,
                                    api_key=api_key,
                                    http_referer=http_referer,
                                    logger=self.log,
                                )
                            )
                            loop.close()
                        
                        if providers:
                            existing_only = provider.get("only")
                            if isinstance(existing_only, list):
                                merged = []
                                seen = set()
                                for entry in list(existing_only) + providers:
                                    if not isinstance(entry, str):
                                        continue
                                    cleaned = entry.strip()
                                    if not cleaned or cleaned in seen:
                                        continue
                                    seen.add(cleaned)
                                    merged.append(cleaned)
                                provider["only"] = merged
                            else:
                                provider["only"] = providers
                            self.log.debug(
                                "ZDR filter: Set provider.only=%s for model %s",
                                providers,
                                model_id,
                            )
                        else:
                            self.log.debug(
                                "ZDR filter: No ZDR providers found for model %s",
                                model_id,
                            )
                    except Exception as exc:
                        self.log.warning(
                            "ZDR filter: Failed to fetch providers for model %s: %s",
                            model_id,
                            exc,
                        )
                else:
                    self.log.debug("ZDR filter: OPENROUTER_API_KEY not set, skipping provider.only")
            elif not aiohttp:
                self.log.warning("ZDR filter: aiohttp not available, cannot fetch ZDR providers")
            
            self.log.debug("ZDR filter: Enforcing Zero Data Retention mode")

        return body
