import json
import os
from typing import Any
from dotenv import load_dotenv
import requests

from modules.definitions import ROOT

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
        self._url = os.environ.get('SAIGA_URL')

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

    def __call__(self, user_question:str, 
                 temperature: float = .015,
                 top_p: float  = .5,
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
        formatted_prompt = {'system': self._system_prompt,
                            'user': user_question,
                            'context': self._context,
                            'temperature': temperature, 
                            'top_p': top_p}
        response = requests.post(url=self._url, json=formatted_prompt)
        if kwargs.get('as_json'):
            return json.loads(response.text)['response']
        else:
            return response.text
        