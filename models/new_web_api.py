import json
from typing import Any
import requests

import models.web_api as web_api
import uuid


class NewWebAssistant(web_api.WebAssistant):
    """Extends base """
    def __call__(
        self, user_question: str,
        temperature: float = .015,
        top_p: float = .5,
        token_limits: int = 8000,
        *args: Any,
        ** kwargs: Any
    ) -> str:
        """Get a response from model for given question.

        Args:
            user_question (str): A user's prompt. Question that requires an answer.
            temperature (float, optional): Generation temperature.
            The higher ,the less stable answers will be. Defaults to 0.015.
            top_p (float, optional): Nuclear sampling. Selects the most likely tokens from a probability distribution,
            considering the cumulative probability until it reaches a predefined threshold “top_p”. Defaults to 0.5.
            token_limits (int): Maximum number of tokens, that can be returned from app
        Returns:
            str: Model's answer to user's question.
        """
        job_id = str(uuid.uuid4())
        content = f'<|begin_of_text|><|start_header_id|>system<|end_header_id|> {self._system_prompt} <|eot_id|><|start_header_id|>user<|end_header_id|> Question: {user_question} Context: {self._context} <|eot_id|><|start_header_id|>assistant<|end_header_id|>'
        formatted_prompt = {
            "job_id": job_id,
            "meta": {
                "temperature": temperature,
                "tokens_limit": token_limits,
                "stop_words": [
                    "string"
                ]
            },
            "content": content
        }
        response = requests.post(url=self._url, json=formatted_prompt)
        if kwargs.get('as_json'):
            try:
                res = json.loads(response.text)['content'].split('ОТВЕТ: ')[1]
            except:
                res = json.loads(response.text)['content']
            return res
        else:
            return response.text
