import logging
import os
from pathlib import Path
from typing import List

from agents.agent import Agent
from agents.prompts import fc_sys_prompt
from agents.prompts import fc_user_prompt
from agents.tools.accessibility_tools import accessibility_tools
from modules.models.connector_creator import LanguageModelCreator
from modules.variables import ROOT
from modules.variables.prompts import *
from utils.measure_time import Timer


path_to_config = Path(ROOT, "config.env")
logger = logging.getLogger(__name__)


# TODO: move this to api module/tools
def define_default_functions(type: str, id: str, coordinates: List) -> List[str]:
    """Selects default functions based on the territory type."""
    default_funcs = []
    if type == "city":
        default_funcs.append("get_general_stats_city")
    elif type == "municipality" or type == "district":
        default_funcs.append("get_general_stats_districts_mo")
    elif type is None and id is not None and coordinates is None:
        default_funcs.append("get_general_stats_block")
    return default_funcs


# TODO: move this to api module/tools
def set_default_value_if_empty(res_funcs: List[str]) -> List[str]:
    """Sets a default value in case no functions were selected by the LLM."""
    if not res_funcs:
        res_funcs.append("get_general_stats_city")
    logger.info(f"Selected functions: {res_funcs}")
    return res_funcs


def service_accessibility_pipeline(
    question: str, coordinates: List, t_type: str, t_id: str
) -> str:
    """Pipeline designed to handle service accessibility data.
    Uses a function calling LLM to choose the correct data source
    to collect the context for the given question. Extracts the
    context and passes it to another LLM to answer the question.

    Args:
        question: A question from the user.
        coordinates: The coordinates of the territory selected on the map.
        t_type: The type of territory that was selected on the map.
        t_id: The name of selected territory.

    Returns: Answer to the question.
    """
    agent = Agent("LLAMA_FC_URL", accessibility_tools)
    with Timer() as t:
        res_funcs = agent.choose_functions(question, fc_sys_prompt, fc_user_prompt)
        logger.info(f"Function choose time: {t.seconds_from_start} sec")
    # with Timer() as t:
    #     res_funcs = agent.check_functions(
    #         question, llm_res_funcs, base_sys_prompt, ac_cor_user_prompt
    #     )
    #     logger.info(f"Function check time: {t.seconds_from_start} sec")
    res_funcs = define_default_functions(t_type, t_id, coordinates) + res_funcs
    res_funcs = set_default_value_if_empty(res_funcs)

    with Timer() as t:
        context = agent.retrieve_context_from_api(t_id, t_type, coordinates, res_funcs)
        logger.info(f"Context retrieve time: {t.seconds_from_start} sec")

    model_url = os.environ.get("LLAMA_URL")
    model_connector = LanguageModelCreator.create_llm_connector(
        model_url, accessibility_sys_prompt
    )
    with Timer() as t:
        response = model_connector.generate(question, context)
        logger.info(f"Answer generation time: {t.seconds_from_start} sec")

    return response
