import logging
from pathlib import Path
from typing import List

from agents.agent import Agent
from agents.prompts import base_sys_prompt
from agents.prompts import binary_fc_user_prompt
from agents.prompts import fc_sys_prompt
from agents.prompts import pip_cor_user_prompt
from agents.tools.pipeline_tools import pipeline_tools
from modules.models.new_web_api import *
from modules.variables.definitions import ROOT
from pipelines import accessibility_pipeline
from pipelines import strategy_pipeline


def get_relevant_function_from_llm(model_url: str, tools: List, question: str) -> str:
    params = {
        "messages": [
            {
                "role": "system",
                "content": f"You are a helpful assistant with access to the following functions. "
                f"Use them if required - {str(tools)}.",
            },
            {
                "role": "user",
                "content": f"Extract all relevant data for answering this question: "
                f"{question}\n"
                f"You MUST return ONLY the function name. "
                # f"You MUST return ONLY the function call with parameters. "
                f"Do NOT return any other additional text.",
            },
        ]
    }
    response = requests.post(url=model_url, json=params)
    res = json.loads(response.text)
    return res["choices"][0]["message"]["content"]


def parse_function_names_from_check_llm_answer_for_metrics(llm_res: str) -> List:
    match = re.search(r"^\[Correct answer\]:.*", llm_res, re.MULTILINE)
    res = []
    if match:
        correct_answer_line = match.group(0)
        if "service_accessibility_pipeline" in correct_answer_line:
            res.append("api")
        if "strategy_development_pipeline" in correct_answer_line:
            res.append("rag")
    return res


def parse_function_names_from_check_llm_answer(llm_res: str) -> List:
    match = re.search(r"^\[Correct answer\]:.*", llm_res, re.MULTILINE)
    res = []
    if match:
        correct_answer_line = match.group(0)
        if "service_accessibility_pipeline" in correct_answer_line:
            res.append("service_accessibility_pipeline")
        if "strategy_development_pipeline" in correct_answer_line:
            res.append("strategy_development_pipeline")
    return res


def parse_function_names_from_llm_answer(llm_res: str) -> List:
    res = []
    functions = ["service_accessibility_pipeline", "strategy_development_pipeline"]
    for pipeline_func in functions:
        if pipeline_func in llm_res:
            res.append(pipeline_func)
    return res


def check_choice_correctness(question: str, answer: str, tools: List):
    sys_prompt = (
        "You are a knowledgeable, efficient, and direct AI assistant. Provide concise answers, "
        "focusing on the key information needed. Offer suggestions tactfully when appropriate to "
        "improve outcomes. Engage in productive collaboration with the user."
    )
    model = NewWebAssistant()
    model.set_sys_prompt(sys_prompt)
    user_message = (
        f"[Instruction]: You are given question, descriptions of 2 functions and an answer from another "
        f"Llama model, which has chosen one of these functions. Your task is to compare "
        f"the chosen function with the question and the descriptions and determine "
        f"if the function was selected correctly. If the chosen function is correct, "
        f"return the function name. If the function is selected incorrectly, return the name "
        f"of another function.\n"
        f"[Question]: {question}.\n"
        f"[Answer]: {answer}.\n"
        f"[Function Descriptions]: {tools}.\n"
        f"[Task]: "
        f"Compare the chosen function with the function descriptions and the question "
        f"to determine if the function was selected correctly. Return the name of correct function in this format: "
        f"[Correct answer]: correct function."
    )
    ans = model(user_message, as_json=False)

    return ans


def choose_pipeline(q: str) -> List[str]:
    load_dotenv(ROOT / "config.env")
    model_url = os.environ.get("LLAMA_FC")

    llm_res = get_relevant_function_from_llm(model_url, tools, q)
    res_funcs = parse_function_names_from_llm_answer(llm_res)
    return res_funcs


def check_pipeline(q: str, r_f: List[str]) -> List[str]:
    llm_check_res = check_choice_correctness(q, r_f[0], tools)
    checked_res_funcs = parse_function_names_from_check_llm_answer(llm_check_res)
    return checked_res_funcs


def answer_question_with_llm(
    question: str, coordinates: List, t_type: str, t_id: str, chunk_num: int
) -> str:
    # add loading tools later
    # Send request to agent llm
    res_funcs = choose_pipeline(question)
    checked_res_funcs = check_pipeline(question, res_funcs)


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
        chunk_num: Number of chunks that will be returned by the DB and used as a context.

    Returns: Answer to the question.
    """
    agent = Agent("LLAMA_FC_URL", pipeline_tools)
    res_funcs = agent.choose_functions(question, fc_sys_prompt, binary_fc_user_prompt)
    checked_res_funcs = agent.check_functions(
        question, res_funcs, base_sys_prompt, pip_cor_user_prompt
    )

    # Set a default value if the LLM could not come up with an answer
    if not checked_res_funcs:
        checked_res_funcs.append("strategy_development_pipeline")
    logger.info(f"Selected pipeline: {checked_res_funcs}")

    if checked_res_funcs[0] == "strategy_development_pipeline":
        fun_handle = getattr(strategy_pipeline, checked_res_funcs[0])
        llm_res = str(fun_handle(question, chunk_num))
    elif checked_res_funcs[0] == "service_accessibility_pipeline":
        fun_handle = getattr(accessibility_pipeline, checked_res_funcs[0])
        llm_res = str(fun_handle(question, coordinates, t_type, t_id))

    logger.info(f"Final answer: {llm_res}")

    return llm_res
