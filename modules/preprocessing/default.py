import json

from requests import Response


def llama_70b_postprocessing(response: Response) -> str:
    """Postprocessing function to retrieve text answer from hosted llama response.

    Args:
        response (Response): Recieved model's response.

    Returns:
        str: Processed output containing only answer on asked question.
    """
    return json.loads(response.text)["content"]


def llama_8b_postprocessing(response: Response) -> str:
    """Postprocessing function to retrieve text answer from hosted llama response.

    Args:
        response (Response): Recieved model's response.

    Returns:
        str: Processed output containing only answer on asked question.
    """
    return json.loads(response.text)["choices"][0]["message"]["content"]
