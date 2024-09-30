import json

from requests import Response


def parse_answer(res):
    answer_separator = "ANSWER: "

    if answer_separator in res:
        return res.split(answer_separator)[1].strip()
    else:
        return res


def llama_70b_postprocessing(response: Response) -> str:
    """Postprocessing function to retrieve text answer from hosted llama response.

    Args:
        response (Response): Recieved model's response.

    Returns:
        str: Processed output containing only answer on asked question.
    """
    return parse_answer(json.loads(response.text)["content"])


def llama_8b_postprocessing(response: Response) -> str:
    """Postprocessing function to retrieve text answer from hosted llama response.

    Args:
        response (Response): Recieved model's response.

    Returns:
        str: Processed output containing only answer on asked question.
    """
    return parse_answer(json.loads(response.text)["choices"][0]["message"]["content"])


def vsegpt_postprocessing(response: Response) -> str:
    """Postprocessing function to retrieve text answer from vsegpt service.

    Args:
        response (Response): Recieved model's response.

    Returns:
        str: Processed output containing only answer on asked question.
    """
    return parse_answer(response.choices[0].message.content)
