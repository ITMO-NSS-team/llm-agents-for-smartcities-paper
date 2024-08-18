import logging
import os
from pathlib import Path
import re
from typing import List

from dotenv import load_dotenv
from Levenshtein import distance as levenshtein_distance
import requests
from pathlib import Path
from typing import List

from models.definitions import ROOT
from models.new_web_api import *
import pipelines
from pipelines.tools.master_tools import tools
from agents.agent import Agent
from agents.prompts import fc_sys_prompt_template, binary_fc_user_prompt_template, \
                           base_sys_prompt, pip_cor_user_prompt_template
from agents.tools.pipeline_tools import pipeline_tools
from models.definitions import ROOT
from pipelines.accessibility_pipeline import service_accessibility_pipeline
from pipelines.strategy_pipeline import strategy_development_pipeline



path_to_config = Path(ROOT, "config.env")
logger = logging.getLogger(__name__)


def answer_question_with_llm(question: str,
                             coordinates: List,
                             t_type: str,
                             t_id: str,
                             chunk_num: int) -> str:
    """ Chooses and runs all pipelines that are required to get
    the answer to the users question.

    Args:
        question: a question from the user
        coordinates: the coordinates of the territory selected on the map
        t_type: the type of territory that was selected on the map
        t_id: the name of selected territory
        chunk_num: number of chunks that will be returned by the DB and used as a context

    Returns: answer to the question
    """
    agent = Agent('LLAMA_FC_URL', pipeline_tools)
    res_funcs = agent.choose_functions(question, fc_sys_prompt_template, binary_fc_user_prompt_template)
    checked_res_funcs = agent.check_functions(question, res_funcs, base_sys_prompt, pip_cor_user_prompt_template)

    # Set a default value if the LLM could not come up with an answer TODO: move the function names to tools?
    if not checked_res_funcs:
        checked_res_funcs.append("strategy_development_pipeline")
    logger.info(f"Selected pipeline: {checked_res_funcs}")

    # TODO: think how to handle multiple replies from llm
    if checked_res_funcs[0] == 'strategy_development_pipeline':
        fun_handle = getattr(pipelines.strategy_pipeline, checked_res_funcs[0])
        llm_res = str(fun_handle(question, chunk_num))
    elif checked_res_funcs[0] == 'service_accessibility_pipeline':
        fun_handle = getattr(pipelines.accessibility_pipeline, checked_res_funcs[0])
        llm_res = str(fun_handle(question, coordinates, t_type, t_id))

    logger.info(f"Final answer: {llm_res}")

    return llm_res


if __name__ == "__main__":
    question = 'Какие проблемы демографического развития Санкт-Петербурга?'
    chunk_num = 4
    ttype = 'city'
    t_id = 'saint-petersburg'
    coords = [
        [
            [30.2679419, 60.1126515],
            [30.2679786, 60.112752],
            [30.2682489, 60.1127275],
            [30.2682122, 60.112627],
            [30.2679419, 60.1126515],
        ]
    ]
    print(answer_question_with_llm(question, coords, None, None, chunk_num))
