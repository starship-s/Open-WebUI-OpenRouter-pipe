"""
title: ZDR (Zero Data Retention)
author: starship-s
author_url: https://github.com/starship-s/Open-WebUI-OpenRouter-pipe
id: openrouter_zdr_filter
description: Enforces Zero Data Retention mode on all OpenRouter requests. Only ZDR-compliant providers will be used.
version: 0.2.0
license: MIT
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from open_webui.env import SRC_LOG_LEVELS
except ImportError:
    SRC_LOG_LEVELS = {}

OWUI_OPENROUTER_PIPE_MARKER = "openrouter_pipe:zdr_filter:v1"
_FEATURE_FLAG = "zdr"


class Filter:
    """
    Zero Data Retention filter for OpenRouter requests.
    
    When enabled, this filter sets provider.zdr=true on all requests,
    ensuring that only ZDR-compliant providers are used. This is useful
    for compliance with data retention policies.
    
    This filter enforces ZDR on requests. To also HIDE non-ZDR models from
    the model list, enable the HIDE_MODELS_WITHOUT_ZDR valve on the pipe itself
    (Admin -> Functions -> [OpenRouter Pipe] -> Valves).
    
    See: https://openrouter.ai/docs/provider-routing
    """
    
    # Toggleable filter (shows a switch in the Integrations menu).
    # Set to True so users can disable ZDR per-chat if needed.
    toggle = True

    def __init__(self) -> None:
        self.log = logging.getLogger("openrouter.zdr.filter")
        self.log.setLevel(SRC_LOG_LEVELS.get("OPENAI", logging.INFO))
        self.toggle = True

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
            self.log.debug("ZDR filter: Enforcing Zero Data Retention mode")

        return body
