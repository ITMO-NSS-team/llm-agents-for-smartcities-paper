from abc import ABCMeta
from abc import abstractmethod
import os
import uuid

from dotenv import load_dotenv
from openai import OpenAI
import requests

from modules.preprocessing.text_preprocessor import TextProcessorInterface
from modules.variables import ResponseMode
from modules.variables import ROOT


class BaseLanguageModelInterface(metaclass=ABCMeta):
    """Base interface of a LLM connector."""

    def __init__(self, sys_prompt: str) -> None:
        """Initialize an instance of LLM connector. And read environment variables from config file.

        Args:
            sys_prompt (str): System instructions for the model.
        """
        load_dotenv(ROOT / "config.env")
        self._system_prompt = sys_prompt

    @property
    def system_prompt(self) -> str:
        """Return model's instructions by system.

        Returns:
            str: Main instructions how to answer to given prompts.
        """
        return self._system_prompt

    def set_system_prompt(self, sys_prompt: str) -> None:
        """Override current system prompt with a new one.

        Args:
            sys_prompt (str): New system instructions to the model.
        """
        self._system_prompt = sys_prompt

    @staticmethod
    def prep_context(context: str) -> str:
        """Preps context so that it can be inserted into a JSON structure."""
        return context.replace('"', "'")

    @abstractmethod
    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """This method takes user question(prompt) with context. A tries to find an answer to given question with LLM.

        Args:
            prompt (str): User's question.
            context (str): Additional data containing information related to the question.
        """
        raise NotImplementedError


class WEBLanguageModel(BaseLanguageModelInterface):
    """Implementation of Large Language Model's connector.
    Intended for work with LLMs hosted in web services.
    """

    def __init__(
        self,
        sys_prompt: str,
        address: str,
        text_processor: TextProcessorInterface,
        **kwargs,
    ) -> None:
        """Initialize an instance of a LLM  with system prompt and address where model is hosted.

        Args:
            sys_prompt (str): Model's system instructions,
            such as model role, base bahavior instructions, etc.. Defaults to None.
            address (str): Address where LLM is hosted.
            Will be used for getting answers from LLM on given question. Defaults to None.
            text_processor: An object responsible for prompt and response processing for the required format. Defaults to None.
        """
        super().__init__(sys_prompt)
        self.text_processor = text_processor
        self._url = address
        self._additional_parameters = kwargs

    @property
    def url(self) -> str:
        """Returns url address for requests to hosted model.

        Returns:
            Optional[str]: URL address.
        """
        return self._url

    def set_url(self, new_address: str) -> None:
        """Override current model url with new one.

        Args:
            new_address (str): model's new url address.
        """
        self._url = new_address

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.15,
        top_k: int = 50,
        top_p: float = 0.15,
        mode: ResponseMode = ResponseMode.default,
        **kwargs,
    ) -> str | requests.Response:
        """Get a response from the model on a given prompt.

        Args:
            prompt (str): User prompt.
            context (Optional[str], optional): Additional information to respond to the user's prompt. Defaults to None.
            temperature (float, optional): Generation temperature. Responsible for response's randomness.
            The higher the temperature is, the less deterministic answer will be. Defaults to 0.15.
            top_k (int, optional): Amount of tokens that are considered while sampling. Defaults to 50.
            top_p (float, optional): Parameter to manage randomness of the LLM output.
            Responsible for selecting tokens whose combined likelihood surpasses this threshold. Defaults to 0.15.
            mode (ResponseMode): Determines in what form model response will be received. For mode "default",
            response will be in string format and contain only the answer to the question, whilst with mode "full"
            answer will be returned as requests.Response object.

        Returns:
            Union[str, request.Response]: LLM's response for given prompt.
        """
        job_id = str(uuid.uuid4())
        token_limit = kwargs.get("tokens_limit", 64000)
        if context is None:
            formatted_prompt = f"Question: {prompt}"
        else:
            formatted_prompt = f"Context: {self.prep_context(context)} Question: {prompt}"

        message = self.text_processor.preprocess_input(
            job_id=str(job_id),
            temperature=str(temperature),
            token_limit=str(token_limit),
            top_p=str(top_p),
            top_k=str(top_k),
            system_prompt=str(self.system_prompt),
            user_prompt=str(formatted_prompt),
        )
        response = requests.post(url=self.url, json=message)
        match mode:
            case ResponseMode.full:
                return response
            case ResponseMode.default:
                return self.text_processor.preprocess_output(response)


class GPTWebLanguageModel(BaseLanguageModelInterface):
    """Class connector for invoking LLM calls from third-party services."""

    def __init__(
        self, sys_prompt: str, model_name: str, text_processor: TextProcessorInterface
    ) -> None:
        super().__init__(sys_prompt)
        self.text_processor = text_processor
        self._model_name = model_name
        self._model = OpenAI(
            api_key=os.environ.get("VSE_GPT_KEY"), base_url="https://api.vsegpt.ru/v1"
        )

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.15,
        top_k: int = 50,
        top_p: float = 0.15,
        **kwargs,
    ) -> str:
        """Get a response from the model on a given prompt.

        Args:
            prompt (str): User prompt.
            context (Optional[str], optional): Additional information to respond to the user's prompt. Defaults to None.
            temperature (float, optional): Generation temperature. Responsible for response's randomness.
            The higher the temperature is, the less deterministic answer will be. Defaults to 0.15.
            top_k (int, optional): Amount of tokens that are considered while sampling. Defaults to 50.
            top_p (float, optional): Parameter to manage randomness of the LLM output.
            Responsible for selecting tokens whose combined likelihood surpasses this threshold. Defaults to 0.15.

        Returns:
            str: LLM's response for given prompt.
        """
        if context is None:
            prompt = f"Question: {prompt}"
        else:
            prompt = f"Context: {self.prep_context(context)}. Question: {prompt}"
        message = self.text_processor.preprocess_input(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )
        response = self._model.chat.completions.create(
            model=self._model_name,
            messages=message,
            temperature=temperature,
            max_tokens=kwargs.get("max_tokes", 8000),
        )
        return self.text_processor.preprocess_output(response)
