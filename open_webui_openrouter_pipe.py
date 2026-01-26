"""
title: Open WebUI OpenRouter Responses Pipe (ZDR Fork)
author: starship-s
author_url: https://github.com/starship-s
git_url: https://github.com/starship-s/Open-WebUI-OpenRouter-pipe
id: open_webui_openrouter_pipe
description: OpenRouter Responses API pipe with ZDR enforcement and custom features
required_open_webui_version: 0.7.0
version: 2.0.27-zdr
requirements: git+https://github.com/starship-s/Open-WebUI-OpenRouter-pipe.git@main
license: MIT

This is a fork of rbb-dev/Open-WebUI-OpenRouter-pipe with:
- ZDR (Zero Data Retention) enforcement
<<<<<<< HEAD
- HIDE_MODELS_WITHOUT_ZDR valve
- ZDR_EXCLUDED_PROVIDERS valve
- ENFORCE_DATA_COLLECTION_DENY valve
=======
>>>>>>> ada637a (Remove ZDR model hiding and attach filter globally)
- Task model overrides (TASK_TITLE_MODEL_ID, TASK_FOLLOWUP_MODEL_ID)
- Model icon overrides (MODEL_ICON_OVERRIDES)

"""

from open_webui_openrouter_pipe import Pipe as BasePipe

_MODULE_PREFIX = "function_"
_runtime_id = __name__[len(_MODULE_PREFIX) :] if __name__.startswith(_MODULE_PREFIX) else BasePipe.id


class Pipe(BasePipe):
    id = _runtime_id

__all__ = ["Pipe"]
