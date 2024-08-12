from abc import ABCMeta, abstractmethod
from types import NotImplementedType
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import requests

from models.definitions import ROOT


class BaseLanguageModel(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, prompt: str, context: str, **kwargs) -> Any:
        """This method takes user question(prompt) with context. A tries to find an answer to given question with LLM.

        Args:
            prompt (str): User's question.
            context (str): Additional data containing information related to the question.
        """
        raise NotImplementedType


class DefaultWEBLanguageModel(BaseLanguageModel):
    """
    Base implementation of Large Language Model's connector. 
    Intended for work with LLMs hosted in web services.
    """

    def __init__(self, sys_prompt: str, address: str, prompt_template: str, **kwargs) -> None:
        """Initialize an instance of a LLM  with system prompt and address where model is hosted.

        Args:
            sys_prompt (str): Model's system instructions, 
            such as model role, base bahavior instructions, etc.. Defaults to None.
            address (str): Address where LLM is hosted. 
            Will be used for getting answers from LLM on given question. Defaults to None.
            prompt_template (str): Model specific prompt template.
        """
        load_dotenv(ROOT / 'config.env')
        self._system_prompt = sys_prompt
        self._url = address
        self._additional_parameters = kwargs

    @property
    def system_prompt(self) -> Optional[str]:
        """Returns current system prompt.

        Returns:
            Optional[str]: Current system prompt.
        """
        return self._system_prompt

    @property
    def url(self) -> Optional[str]:
        """Returns url address for requests to hosted model.

        Returns:
            Optional[str]: URL address.   
        """
        return self._url

    def _generate_prompt(self, user_message: str, context: Optional[str] = '') -> Dict:
        """Preprocess system prompt, given user message and context for LLM specific prompt format"""
        user_prompt = f'Question: {user_message}, Context: {context}.'
        prompt = PromptTemplate(input_variables=["system_prompt", "user_prompt"])
        return prompt.format(system_prompt=self.system_prompt, user_prompt=user_prompt)

    def set_sys_prompt(self, sys_prompt: str) -> None:
        """Override current system prompt with new one.

        Args:
            sys_prompt (str): new system prompt.
        """
        self._system_prompt = sys_prompt

    def set_url(self, new_address: str) -> None:
        """Override current model url with new one.

        Args:
            new_address (str): model's new url address.
        """
        self._url = new_address

    def generate(self,
                 prompt: str,
                 context: Optional[str] = '',
                 temperature: float = .15,
                 top_k: int = 50,
                 top_p: float = .15,
                 **kwargs) -> Any:
        formatted_prompt = self._generate_prompt(
            user_message=prompt, context=context)
        response = requests.post(url=self.url, json=formatted_prompt)
        
