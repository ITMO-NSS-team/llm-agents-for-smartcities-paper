import logging
import os
from pathlib import Path
from string import Template
from typing import Dict, List

from dotenv import load_dotenv
from Levenshtein import distance as levenshtein_distance

import api.summary_tables_requests
from api.utils.coords_typer import prepare_typed_coords
from modules.models.connector_creator import LanguageModelCreator
from modules.variables import ROOT


path_to_config = Path(ROOT, "config.env")
logger = logging.getLogger(__name__)


class Agent:
    """A class that represents an LLM agent that can work with any type of input data."""

    def __init__(self, fc_llm_name: str, tools: List[Dict]) -> None:
        """Creates an Agent object.

        Args:
            fc_llm_name: URL of the function calling LLM.
            tools: A list of tools for the FC LLM to choose from.
        """
        load_dotenv(path_to_config)
        self.model_url = os.environ.get(fc_llm_name)
        self.tools = tools
        self.functions = [tool["function"]["name"] for tool in tools]
        # TODO: pass model as a param

    @staticmethod
    def get_nearest_levenstein(string: str, correct_strings: List[str]) -> str:
        """Returns the most similar correct string from the list for the given string."""
        return min(correct_strings, key=lambda x: levenshtein_distance(string, x))

    def parse_function_names_from_agent_answer(self, llm_res: str) -> List[str]:
        """Finds function names (from the current tools) in the LLM answer."""
        predicted_funcs = llm_res.replace("[Correct answer]: ", "").split(" ")
        predicted_funcs = list(map(lambda x: x.strip(), predicted_funcs))
        correct_pred_funcs = set(
            map(
                lambda x: self.get_nearest_levenstein(x, self.functions),
                predicted_funcs,
            )
        )
        res = list(correct_pred_funcs.intersection(self.functions))
        return res

    @staticmethod
    def retrieve_context_from_api(
        t_name: str, t_type: str, coords: List, chosen_functions: List
    ) -> str:
        """Call all functions to get the context.

        Calls all given functions in order to collect the relevant context
        for the given question.

        Args:
            t_name: Name of the chosen territory.
            t_type: Type of the chosen territory.
            coords: List of coordinates for the chosen territory.
            chosen_functions: Functions from the API module.

        Returns: The results of all functions combined into one string.
        """
        if coords:
            coordinates = prepare_typed_coords(coords)
        else:
            coordinates = None
        chosen_functions = chosen_functions[:3]
        context = ""
        try:
            for func in chosen_functions:
                cur_handle = getattr(api.summary_tables_requests, func)
                context += str(
                    cur_handle(
                        name_id=t_name, territory_type=t_type, coordinates=coordinates
                    )
                )
        except Exception as e:
            # TODO: send these logs to frontend
            logger.error(f"Could NOT retrieve context from API: {e}")
        return context

    def get_relevant_functions(
        self, question: str, sys_prompt: str, user_prompt: str
    ) -> List[str]:
        """Send request to get suitable functions.

        Sends a request to a function calling LLM to choose the most suitable
        functions to get the context for the given question. Possible functions
        must be defined in the current tools.

        Args:
            question: The user's question.
            sys_prompt: System prompt for the current tools.
            user_prompt: User prompt for the current tools.

        Returns: List of the most suitable functions.
        """
        sys_prompt = Template(sys_prompt).safe_substitute(
            tools=str(self.tools).replace('"', "'")
        )
        user_prompt = Template(user_prompt).safe_substitute(question=question)
        model_connector = LanguageModelCreator.create_llm_connector(
            self.model_url, sys_prompt
        )
        return model_connector.generate(user_prompt)

    def choose_functions(
        self, question: str, sys_prompt: str, user_prompt: str
    ) -> List[str]:
        """Chose function to get the context for given question.

        Chooses the most suitable functions to get the context for the given question.
        """
        llm_res = self.get_relevant_functions(question, sys_prompt, user_prompt)
        llm_res_funcs = self.parse_function_names_from_agent_answer(llm_res)
        return llm_res_funcs

    def check_choice_correctness(
        self,
        question: str,
        answer: str | List[str],
        sys_prompt: str,
        user_prompt: str,
    ) -> str:
        """Check the chosen list of functions.

        Checks if the list of functions returned by the LLM is accurate. If it is not,
        returns a better choice for the given question. The validation is done
        by another LLM.

        Args:
            question: The user's question.
            answer: Parsed response from the function calling LLM.
            sys_prompt: System prompt for checking chosen functions.
            user_prompt: User prompt for checking chosen functions.

        Returns: A string that contains the corrected names of the chosen
        functions in a free format.
        """
        user_prompt = Template(user_prompt).safe_substitute(
            question=question, answer=answer, tools=str(self.tools).replace('"', "'")
        )
        model_connector = LanguageModelCreator.create_llm_connector(
            self.model_url, sys_prompt
        )
        return model_connector.generate(user_prompt)

    def check_functions(
        self,
        question: str,
        answer: str | List[str],
        sys_prompt: str,
        user_prompt: str,
    ) -> List[str]:
        """Corrects the list of functions returned by the function calling LLM."""
        llm_check_res = self.check_choice_correctness(
            question, answer, sys_prompt, user_prompt
        )
        return self.parse_function_names_from_agent_answer(llm_check_res)
