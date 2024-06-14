from typing import Any
import json


def get_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return json.dumps(content) if content else ""
    else:
        return str(content) if content is not None else ""
