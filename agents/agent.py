import logging
import os
from dotenv import load_dotenv
from Levenshtein import distance as levenshtein_distance
from pathlib import Path
from string import Template
from typing import Dict, List

import api.summary_tables_requests
from models.definitions import ROOT
from models.new_web_api import *


path_to_config = Path(ROOT, 'config.env')
logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, fc_llm_name: str, tools: List[Dict]) -> None:
        load_dotenv(path_to_config)
        self.model_url = os.environ.get(fc_llm_name)
        self.tools = tools
        self.functions = [tool['function']['name'] for tool in tools]
        # TODO: pass model as a param

    @staticmethod
    def get_nearest_levenstein(string: str, correct_strings: List[str]) -> str:
        """Returns the most similar correct string from the list for the given string."""
        return min(correct_strings, key=lambda x: levenshtein_distance(string, x))

    def parse_function_names_from_agent_answer(self, llm_res: str) -> List[str]:
        """Finds function names (from the current tools) in the LLM answer."""
        predicted_funcs = llm_res.replace('[Correct answer]: ', '').split(' ')
        predicted_funcs = list(map(lambda x: x.strip(), predicted_funcs))
        correct_pred_funcs = set(map(lambda x: self.get_nearest_levenstein(x, self.functions), predicted_funcs))
        res = list(correct_pred_funcs.intersection(self.functions))
        return res

    # TODO: move to api module
    def get_dimensions(self, lst: List[str]) -> int:
        if isinstance(lst, list):
            return 1 + max(self.get_dimensions(item) for item in lst)
        else:
            return 0

    # TODO: move to api module
    def get_territory_coordinate_type(self, coords: List) -> str:
        n_dims = self.get_dimensions(coords)
        if n_dims >= 3:
            return 'MultiPolygon'
        elif n_dims == 2:
            return 'Polygon'
        elif n_dims == 1:
            return 'Point'
        else:
            raise Exception(f'Unexpected coordinates dims: {n_dims}')

    def retrieve_context_from_api(self, coords: List, chosen_functions: List) -> str:
        """Calls all given functions in order to collect the relevant context
        for the given question.

        Args:
            coords: List of coordinates for a specific area.
            chosen_functions: Functions from the API module.

        Returns: The results of all functions combined into one string.
        """
        coords_type = self.get_territory_coordinate_type(coords)
        input_data = {"coordinates": coords, "type": coords_type}  # TODO: move to api module
        context = ''
        try:
            for func in chosen_functions:
                cur_handle = getattr(api.summary_tables_requests, func)
                context += str(cur_handle(input_data))
        except Exception as e:
            # TODO: send these logs to frontend
            logger.error(f'Could NOT retrieve context from API: {e}')
        return context

    def get_relevant_functions(self, question: str,
                               sys_prompt: str,
                               user_prompt: str) -> List[str]:
        """Sends a request to a function calling LLM to choose the most suitable functions
        to get the context for the given question. Possible functions must be defined in the
        current tools.

        Args:
            question: The user's question.
            sys_prompt: System prompt for the current tools.
            user_prompt: User prompt for the current tools.

        Returns: List of the most suitable functions.

        TODO: use new connector from model module
        """
        params = {
            "messages": [
                {
                    "role": "system",
                    "content":  Template(sys_prompt).safe_substitute(tools=str(self.tools))
                },
                {
                    "role": "user",
                    "content": Template(user_prompt).safe_substitute(question=question)
                }
            ]
        }
        response = requests.post(url=self.model_url, json=params)
        res = json.loads(response.text)
        return res['choices'][0]['message']['content']

    def choose_functions(self, question: str, sys_prompt: str, user_prompt: str) -> List[str]:
        """Chooses the most suitable functions to get the context for the given question."""
        llm_res = self.get_relevant_functions(question, sys_prompt, user_prompt)
        llm_res_funcs = self.parse_function_names_from_agent_answer(llm_res)
        return llm_res_funcs

    # TODO: move to another location
    @staticmethod
    def generate_llm_answer(question: str, system_prompt: str, context: str, as_json: bool = True) -> str:
        """Calls LLM with correct params and returns the answer."""
        model = NewWebAssistant()
        model.set_sys_prompt(system_prompt)
        model.add_context(context)
        response = model(question, as_json=as_json)
        return response

    def check_choice_correctness(self, question: str, answer: str | List[str],
                                 sys_prompt: str, user_prompt: str) -> str:
        """Checks if the list of functions returned by the LLM is accurate. If it is not,
        returns a better choice for the given question. The validation is done by another LLM.

        Args:
            question: The user's question.
            answer: Parsed response from the function calling LLM.
            sys_prompt: System prompt for checking chosen functions.
            user_prompt: User prompt for checking chosen functions.

        Returns: A string that contains the corrected names of the chosen functions in a free format.
        """
        user_message = Template(user_prompt).safe_substitute(question=question, answer=answer, tools=self.tools)
        return self.generate_llm_answer(user_message, sys_prompt, '', False)

    def check_functions(self, question: str, answer: str | List[str],
                        sys_prompt: str, user_prompt: str) -> List[str]:
        """Corrects the list of functions returned by the function calling LLM."""
        llm_check_res = self.check_choice_correctness(question, answer, sys_prompt, user_prompt)
        return self.parse_function_names_from_agent_answer(llm_check_res)
