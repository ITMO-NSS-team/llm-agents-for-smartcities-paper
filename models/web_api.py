import json
import os
from typing import Any
from dotenv import load_dotenv
import requests

from models.definitions import ROOT


class WebAssistant:
    """
    Web implementation of LLM assistant for answering urbanistic questions.
    """

    def __init__(self) -> None:
        """
        Initialize an instanse of LLM assistant.
        """
        load_dotenv(ROOT / 'config.env')
        self._system_prompt = None
        self._context = None
        self._url = os.environ.get('LLAMA_URL')

    def set_sys_prompt(self, new_prompt: str) -> None:
        """Set model's role and generation instructions.

        Args:
            new_prompt (str): New instructions.
        """
        self._system_prompt = new_prompt

    def add_context(self, context: str) -> None:
        """Add a context to model's prompt

        Args:
            context (str): context related to question.
        """
        self._context = context

    def __call__(self, user_question: str,
                 temperature: float = .015,
                 top_p: float = .5,
                 *args: Any,
                 **kwargs: Any) -> str:
        """Get a response from model for given question.

        Args:
            user_question (str): A user's prompt. Question that requires an answer.
            temperature (float, optional): Generation temperature. 
            The higher ,the less stable answers will be. Defaults to 0.015.
            top_p (float, optional): Nuclear sampling. Selects the most likely tokens from a probability distribution, 
            considering the cumulative probability until it reaches a predefined threshold “top_p”. Defaults to 0.5.

        Returns:
            str: Model's answer to user's question. 
        """
        formatted_prompt = {
            "messages": [
                {
                    "role": "system",
                    "content": self._system_prompt
                },
                {
                    "role": "user",
                    "content": f"Question: {user_question} Context: {self._context}"
                }
            ]
        }
        response = requests.post(url=self._url, json=formatted_prompt)
        if kwargs.get('as_json'):
            try:
                res = json.loads(response.text)['choices'][0]['message']['content'].split('ANSWER: ')[1]
            except:
                res = json.loads(response.text)['choices'][0]['message']['content']
            return res
        else:
            return response.text
