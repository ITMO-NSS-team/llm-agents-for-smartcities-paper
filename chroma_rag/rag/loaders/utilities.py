import json
from typing import Any


def get_text(content: Any) -> str:
    # Converts content to a string, handling str, dict, and other types appropriately.

    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return json.dumps(content) if content else ""
    else:
        return str(content) if content is not None else ""
