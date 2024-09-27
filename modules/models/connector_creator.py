import urllib

from dotenv import load_dotenv
import requests

from modules.models.connectors import BaseLanguageModelInterface
from modules.models.connectors import GPTWebLanguageModel
from modules.models.connectors import WEBLanguageModel
from modules.preprocessing.default import llama_8b_postprocessing
from modules.preprocessing.default import llama_70b_postprocessing
from modules.preprocessing.default import vsegpt_postprocessing
from modules.preprocessing.text_preprocessor import BaseTextProcessor
from modules.variables import ROOT
from modules.variables.prompts import all_gpt_template
from modules.variables.prompts import llama_8b_template
from modules.variables.prompts import llama_70b_template


load_dotenv(ROOT / "config.env")


class LanguageModelCreator:
    """A class to automatically choose what class and params need to be used
    for the given LLM based on its URL.
    """

    model_settings = {
        "llama-8b": {
            "template": llama_8b_template,
            "postprocessor": llama_8b_postprocessing,
        },
        "llama-70b": {
            "template": llama_70b_template,
            "postprocessor": llama_70b_postprocessing,
        },
    }

    @classmethod
    def _get_model_type(cls, url: str) -> str:
        """Checks the type of the LLM service by requesting the model name from it.

        Args:
            url: The LLM endpoint for making requests.

        Returns: The type of the LLM service.
        """
        url_parts = urllib.parse.urlparse(url)
        url = f"{url_parts.scheme}://{url_parts.netloc}/v1/models"
        res = requests.get(url=url)
        if res.status_code == 200:
            return "llama-8b"
        else:
            return "llama-70b"

    @classmethod
    def create_llm_connector(
        cls, model_url: str, sys_prompt: str
    ) -> BaseLanguageModelInterface:
        """Creates the proper connector for a given LLM service.

        Args:
            model_url: The LLM endpoint for making requests.
            sys_prompt: System prompt.

        Returns: The connector object that can be used to make requests to the LLM service.
        """
        if "vsegpt" in model_url:
            model_name = model_url.split(";")[1]
            message_processor = BaseTextProcessor(all_gpt_template, vsegpt_postprocessing)
            return GPTWebLanguageModel(sys_prompt, model_name, message_processor)
        else:
            model_type = cls._get_model_type(model_url)
            try:
                settings = cls.model_settings[model_type]
            except:
                raise ValueError(f"No settings found for URL: {model_url}")
            message_processor = BaseTextProcessor(
                settings["template"], settings["postprocessor"]
            )
            return WEBLanguageModel(
                sys_prompt, model_url, text_processor=message_processor
            )
