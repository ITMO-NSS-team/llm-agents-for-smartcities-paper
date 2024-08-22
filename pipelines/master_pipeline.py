import logging
from pathlib import Path
from typing import List

import pipelines
from agents.agent import Agent
from agents.prompts import fc_sys_prompt, binary_fc_user_prompt, \
                           base_sys_prompt, pip_cor_user_prompt
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
    """Chooses and runs all pipelines that are required to get
    the answer to the user's question.

    Args:
        question: A question from the user.
        coordinates: The coordinates of the territory selected on the map.
        t_type: The type of territory that was selected on the map.
        t_id: The name of selected territory.
        chunk_num: Number of chunks that will be returned by the DB and used as a context.

    Returns: Answer to the question.
    """
    agent = Agent('LLAMA_FC_URL', pipeline_tools)
    res_funcs = agent.choose_functions(question, fc_sys_prompt, binary_fc_user_prompt)
    checked_res_funcs = agent.check_functions(question, res_funcs, base_sys_prompt, pip_cor_user_prompt)

    # Set a default value if the LLM could not come up with an answer
    if not checked_res_funcs:
        checked_res_funcs.append("strategy_development_pipeline")
    logger.info(f"Selected pipeline: {checked_res_funcs}")

    if checked_res_funcs[0] == 'strategy_development_pipeline':
        fun_handle = getattr(pipelines.strategy_pipeline, checked_res_funcs[0])
        llm_res = str(fun_handle(question, chunk_num))
    elif checked_res_funcs[0] == 'service_accessibility_pipeline':
        fun_handle = getattr(pipelines.accessibility_pipeline, checked_res_funcs[0])
        llm_res = str(fun_handle(question, coordinates, t_type, t_id))

    logger.info(f"Final answer: {llm_res}")

    return llm_res
