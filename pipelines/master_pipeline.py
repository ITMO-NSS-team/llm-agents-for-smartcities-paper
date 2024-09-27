import logging
from pathlib import Path
from typing import List

from agents.agent import Agent
from agents.prompts import binary_fc_user_prompt
from agents.prompts import fc_sys_prompt
from agents.tools.pipeline_tools import pipeline_tools
from modules.variables import ROOT
from pipelines import accessibility_pipeline
from pipelines import strategy_pipeline
from utils.measure_time import Timer


path_to_config = Path(ROOT, "config.env")
logger = logging.getLogger(__name__)


def answer_question_with_llm(
    question: str, coordinates: List, t_type: str, t_id: str, chunk_num: int
) -> str:
    """Chooses and runs all pipelines that are required to get
    the answer to the user's question.

    Args:
        question: A question from the user.
        coordinates: The coordinates of the territory selected on the map.
        t_type: The type of territory that was selected on the map.
        t_id: The name of selected territory.
        chunk_num: Number of chunks that will be returned by the DB and used as
            a context.

    Returns: Answer to the question.
    """
    agent = Agent("LLAMA_FC_URL", pipeline_tools)
    with Timer() as t:
        res_funcs = agent.choose_functions(question, fc_sys_prompt, binary_fc_user_prompt)
        logger.info(f"Pipeline choose time: {t.seconds_from_start} sec")
    # with Timer() as t:
    #     checked_res_funcs = agent.check_functions(
    #         question, res_funcs, base_sys_prompt, pip_cor_user_prompt
    #     )
    #     logger.info(f"Pipeline check time: {t.seconds_from_start} sec")

    # Set a default value if the LLM could not come up with an answer
    if not res_funcs:
        res_funcs.append("strategy_development_pipeline")
    logger.info(f"Selected pipeline: {res_funcs}")

    if res_funcs[0] == "strategy_development_pipeline":
        fun_handle = getattr(strategy_pipeline, res_funcs[0])
        llm_res = str(fun_handle(question, chunk_num))
    elif res_funcs[0] == "service_accessibility_pipeline":
        fun_handle = getattr(accessibility_pipeline, res_funcs[0])
        llm_res = str(fun_handle(question, coordinates, t_type, t_id))

    logger.info(f"Final answer: {llm_res}")

    return llm_res
