import os
import uuid
from abc import ABCMeta, abstractmethod
from types import NotImplementedType
from typing import Any, Dict, Iterable, List, Optional

import requests
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from models.definitions import LARGE_LLAMA, ROOT, SMALL_LLAMA


def get_base_message_form(prompt: str, **kwargs) -> Iterable[ChatCompletionMessageParam]:
    """Build a basic message form for furhter LLM calling. Takes system prompt(optional), prompt and creates request form from them.

    Args:
        prompt (Optional[str], optional): User's question. May include additional context. Defaults to None.

    Raises:
        ValueError: If neither of the prompts were specified.

    Returns:
        List[Dict]: Request form for a LLM calling
    """
    messages = []
    system_prompt = kwargs.get("system_prompt")

    def fun(role, content):
        return {"role": role, "content": content}

    if system_prompt is not None:
        messages.append(fun("system", system_prompt))
    if prompt is not None:
        messages.append(fun("user", prompt))
    return messages


def get_advanced_message_form(prompt: str, **kwargs) -> Dict:
    """Build a message form for LLM calling. Intended to use in cases when prompt includes system insturction, user message and context.

    Args:
        prompt (str): Prompt for LLM. Includes system instruction, user message, and context (if specified). Also can be formatted to LLM required format.

    Returns:
        Dict: Request form for a LLM calling
    """
    messages = {
        "job_id": kwargs.get("job_id", str(uuid.uuid4())),
        "meta": {
            "temperature": kwargs.get("temperature", 0.5),
            "tokens_limit": kwargs.get("token_limits", 8000),
            "stop_words": ["string"],
        },
        "content": prompt,
    }
    return messages


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

    def __init__(
        self,
        sys_prompt: str,
        address: str,
        prompt_template: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize an instance of a LLM  with system prompt and address where model is hosted.

        Args:
            sys_prompt (str): Model's system instructions,
            such as model role, base bahavior instructions, etc.. Defaults to None.
            address (str): Address where LLM is hosted.
            Will be used for getting answers from LLM on given question. Defaults to None.
            prompt_template (str): Model specific prompt template.
        """
        load_dotenv(ROOT / "config.env")
        self._system_prompt = sys_prompt
        self._url = address
        self._additional_parameters = kwargs
        self._prompt_template = prompt_template

    @property
    def system_prompt(self) -> str:
        """Returns current system prompt.

        Returns:
            Optional[str]: Current system prompt.
        """
        return self._system_prompt

    @property
    def url(self) -> str:
        """Returns url address for requests to hosted model.

        Returns:
            Optional[str]: URL address.
        """
        return self._url

    def _generate_prompt(self, user_message: str, context: Optional[str] = "") -> str:
        """Preprocess system prompt, given user message and context for LLM specific prompt format"""
        user_prompt = f"Question: {user_message}, Context: {context}."
        if self._prompt_template is None:
            return user_prompt

        prompt = PromptTemplate(
            input_variables=["system_prompt", "user_prompt"],
            template=self._prompt_template,
        )
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

    def generate(
            self,
            prompt: str,
            context: Optional[str] = "",
            temperature: float = 0.15,
            top_k: int = 50,
            top_p: float = 0.15,
            **kwargs) -> Any:
        job_id = str(uuid.uuid4())
        formatted_prompt = self._generate_prompt(
            user_message=prompt, context=context)

        if self.url == SMALL_LLAMA:
            message = {
                "model": "gpt-3.5-turbo",
                "messages": get_base_message_form(formatted_prompt),
            }
        elif self.url == LARGE_LLAMA:
            message = get_advanced_message_form(prompt,
                                                temperature=temperature,
                                                top_k=top_k,
                                                top_p=top_p,
                                                job_id=job_id,
                                                **kwargs)
        response = requests.post(url=self.url, json=message)
        return response


class GPTWebLanguageModel(DefaultWEBLanguageModel):
    """Class connector for invoking LLM calls from third-party services."""
    def __init__(self, sys_prompt: str, model_name: str) -> None:
        super().__init__(sys_prompt, "https://api.vsegpt.ru/v1")
        self._model_name = model_name
        self._model = OpenAI(api_key=os.environ.get(
            "VSE_GPT_KEY"), base_url=self.url)

    def generate(
            self,
            prompt: str,
            context: str | None = "",
            temperature: float = 0.15,
            top_k: int = 50,
            top_p: float = 0.15,
            **kwargs) -> Optional[str]:
        prompt = self._generate_prompt(
            user_message=prompt, context=context)
        message = get_base_message_form(
            prompt, system_prompt=self.system_prompt)
        response = self._model.chat.completions.create(model=self._model_name,
                                                       messages=message,
                                                       temperature=temperature,
                                                       max_tokens=kwargs.get('max_tokes', 8000))
        return response.choices[0].message.content
