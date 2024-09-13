import os
from pathlib import Path

from deepeval.models.base_model import DeepEvalBaseLLM
from dotenv import load_dotenv
from openai import OpenAI

from modules.variables import ROOT


path_to_config = Path(ROOT, "config.env")


class VseGPTConnector(DeepEvalBaseLLM):
    """Implementation of Evaluation agent based on large language model for Assistant's answers evaluation."""

    def __init__(
        self,
        model: str,
        sys_prompt: str = "",
        base_url="https://api.vsegpt.ru/v1",
    ):
        """Initialize instance with evaluation LLM.

        Args:
            model: Evaluation model's name
            sys_prompt: predefined rules for model
            base_url: URL where models are available
        """
        load_dotenv(path_to_config)
        self._sys_prompt = sys_prompt
        self._model_name = model
        self.base_url = base_url
        self.model = self.load_model()

    def load_model(self) -> OpenAI:
        """Load model's instance."""
        # TODO extend pull of possible LLMs (Not only just OpenAI's models)
        return OpenAI(api_key=os.environ.get("VSE_GPT_KEY"), base_url=self.base_url)

    def generate(
        self,
        prompt: str,
        context: str = None,
        temperature: float = 0.015,
        *args,
        **kwargs,
    ) -> str:
        """Get a response form LLM to given question.

        Args:
            prompt (str): User's question, the model must answer.
            context (str, optional): Supplementary information, may be used for answer.
            temperature (float, optional): Determines randomness and diversity of generated answers.
            The higher the temperature, the more diverse the answer is. Defaults to .015.

        Returns:
            str: Model's response for user's question.
        """
        usr_msg_template = (
            prompt if context is None else f"Вопрос:{prompt} Контекст:{context}"
        )
        formatted_message = [
            {"role": "system", "content": self._sys_prompt},
            {"role": "user", "content": usr_msg_template},
        ]
        response = self.model.chat.completions.create(
            model=self._model_name,
            messages=formatted_message,
            temperature=temperature,
            n=1,
            max_tokens=8182,
        )
        return response.choices[0].message.content

    async def a_generate(
        self,
        prompt: str,
        context: str = None,
        temperature: float = 0.015,
        *args,
        **kwargs,
    ) -> str:
        return self.generate(prompt, context, temperature, *args, **kwargs)

    def get_model_name(self, *args, **kwargs) -> str:
        return "Implementation of custom LLM for evaluation."
