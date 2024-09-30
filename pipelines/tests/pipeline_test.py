import os
from pathlib import Path
import re
from typing import List

from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics import ContextualPrecisionMetric
from deepeval.metrics import ContextualRecallMetric
from deepeval.metrics import ContextualRelevancyMetric
from deepeval.metrics import FaithfulnessMetric
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase
from deepeval.test_case import LLMTestCaseParams
import pandas as pd

from agents.agent import Agent
from agents.prompts import ac_cor_user_prompt
from agents.prompts import base_sys_prompt
from agents.prompts import binary_fc_user_prompt
from agents.prompts import fc_sys_prompt
from agents.prompts import fc_user_prompt
from agents.prompts import pip_cor_user_prompt
from agents.tools.accessibility_tools import accessibility_tools
from agents.tools.pipeline_tools import pipeline_tools
from modules.models.connector_creator import LanguageModelCreator
from modules.models.vsegpt_api import VseGPTConnector
from modules.variables import ROOT
from modules.variables.prompts import accessibility_sys_prompt
from modules.variables.prompts import strategy_sys_prompt
from pipelines.accessibility_pipeline import define_default_functions
from pipelines.accessibility_pipeline import set_default_value_if_empty
from pipelines.strategy_pipeline import retrieve_context_from_chroma
from utils.measure_time import Timer


path_to_data = Path(ROOT, "pipelines", "tests")
strategy_and_access_data = pd.read_csv(
    Path(path_to_data, "test_data", "questions_for_test.csv")
)
strategy_data = pd.read_csv(Path(path_to_data, "test_data", "strategy_questions.csv"))
access_data_simple = pd.read_csv(
    Path(path_to_data, "test_data", "urb_accessibility_questions.csv")
)
strategy_data = strategy_data[strategy_data["correct_answer"].notnull()]
access_data_simple = access_data_simple[access_data_simple["Answer"].notnull()]
collection_name = "strategy-spb"
total_all_questions = strategy_and_access_data.shape[0]
total_strategy_questions = strategy_data.shape[0]
total_access_questions = access_data_simple.shape[0]

model = VseGPTConnector(
    model="openai/gpt-4o-mini"
)  # possible to change model for metric evaluation

metrics_init_params = {
    "model": model,
    "verbose_mode": True,
    "async_mode": False,
}
answer_relevancy = AnswerRelevancyMetric(**metrics_init_params)
faithfulness = FaithfulnessMetric(**metrics_init_params)
context_precision = ContextualPrecisionMetric(**metrics_init_params)
context_recall = ContextualRecallMetric(**metrics_init_params)
context_relevancy = ContextualRelevancyMetric(**metrics_init_params)
correctness_metric = GEval(
    name="Correctness",
    criteria=(
        "Correctness - determine if the actual output is factually "
        "correct according to the expected output."
    ),
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
    **metrics_init_params,
)


def choose_pipeline_test() -> None:
    """Tests pipeline choosing functions.

    Counts number of correctly chosen pipelines and measures elapsed time for
    choosing and checking results.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print("Pipeline choosing test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "pipeline_choose_test_results.txt"
    )
    os.makedirs(os.path.dirname(path_to_results), exist_ok=True)

    total_correct_pipeline = 0
    total_choose_time = 0
    total_check_time = 0

    for i, row in strategy_and_access_data.iterrows():
        question = row["question"]
        correct_pipeline = row["correct_pipeline"]
        print(f"Processing question {i}")
        agent = Agent("LLAMA_FC_URL", pipeline_tools)
        with Timer() as t:
            raw_pipeline = agent.choose_functions(
                question, fc_sys_prompt, binary_fc_user_prompt
            )
            total_choose_time += t.seconds_from_start
        with Timer() as t:
            checked_pipeline = agent.check_functions(
                question, raw_pipeline, base_sys_prompt, pip_cor_user_prompt
            )
            total_check_time += t.seconds_from_start
        if checked_pipeline[0] == correct_pipeline:
            total_correct_pipeline += 1

    corr_pipe_percent = round(total_correct_pipeline / total_all_questions * 100, 2)
    avg_pipe_choose_time = round(total_choose_time / total_all_questions, 2)
    avg_pipe_check_time = round(total_check_time / total_all_questions, 2)

    with open(path_to_results, "w") as f:
        print(
            f"""Percentage of correctly chosen pipeline: {corr_pipe_percent}
Average pipeline choosing time: {avg_pipe_choose_time}
Average pipeline check time: {avg_pipe_check_time}""",
            file=f,
        )


def choose_functions_test() -> None:
    """Tests API functions choosing function.

    Counts number of correctly chosen function and measures elapsed time for
    choosing and checking results.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print("API functions choosing test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "choose_functions_test_results.txt"
    )
    os.makedirs(os.path.dirname(path_to_results), exist_ok=True)

    total_correct_functions = 0
    total_function_choose_time = 0
    total_check_function_time = 0

    for i, row in access_data_simple.iterrows():
        question = row["Question"]
        correct_function = row["Dataset"]
        t_type = row["Territory Type"]
        t_name = row["Territory Name"]
        coordinates = row["Geometry"]
        print(f"Processing question {i}")
        agent = Agent("LLAMA_FC_URL", accessibility_tools)
        with Timer() as t:
            functions = agent.choose_functions(question, fc_sys_prompt, fc_user_prompt)
            total_function_choose_time += t.seconds_from_start
        with Timer() as t:
            corrected_functions = agent.check_functions(
                question, functions, base_sys_prompt, ac_cor_user_prompt
            )
            total_check_function_time += t.seconds_from_start
        final_res = corrected_functions + define_default_functions(
            t_type, t_name, coordinates
        )
        final_res = set_default_value_if_empty(final_res)
        if correct_function in final_res:
            total_correct_functions += 1

    corr_func_percent = round(total_correct_functions / total_access_questions * 100, 2)
    avg_func_choose_time = round(total_function_choose_time / total_access_questions, 2)
    avg_func_check_time = round(total_check_function_time / total_access_questions, 2)

    with open(path_to_results, "w") as f:
        print(
            f"""Percentage of correctly chosen functions: {corr_func_percent}
Average function choosing time: {avg_func_choose_time}
Average function checking time: {avg_func_check_time}""",
            file=f,
        )


def accessibility_pipeline_test() -> None:
    """Tests whole accessibility pipeline.

    Counts the number of correctly chosen functions and correct answers, measures
    elapsed time for choosing and checking and final answer generation.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print("Accessibility pipeline test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "accessibility_pipeline_test_results.txt"
    )
    os.makedirs(os.path.dirname(path_to_results), exist_ok=True)

    correct_function_choice = 0
    correct_accessibility_answer = 0
    total_model_time = 0
    total_function_choose_time = 0
    total_check_function_time = 0
    total_get_context_time = 0

    for i, row in access_data_simple.iterrows():
        print(f"Processing question {i}")
        question = row["Question"]
        correct_answer = row["Answer"]
        correct_function = row["Dataset"]
        t_t = row["Territory Type"]
        t_n = row["Territory Name"]
        cs = row["Geometry"]
        t_type = None if pd.isnull(t_t) else t_t
        if pd.isnull(t_n):
            t_name = None
        else:
            try:
                t_name = int(t_n)
            except ValueError:
                t_name = t_n
        if pd.isnull(cs):
            coordinates = None
        else:
            coordinates = eval(row["Geometry"])["coordinates"]
        agent = Agent("LLAMA_FC_URL", accessibility_tools)
        with Timer() as t:
            functions = agent.choose_functions(question, fc_sys_prompt, fc_user_prompt)
            total_function_choose_time += t.seconds_from_start
        with Timer() as t:
            corrected_functions = agent.check_functions(
                question, functions, base_sys_prompt, ac_cor_user_prompt
            )
            total_check_function_time += t.seconds_from_start
        res_funcs = corrected_functions + define_default_functions(
            t_type, t_name, coordinates
        )
        res_funcs = set_default_value_if_empty(res_funcs)
        with Timer() as t:
            context = agent.retrieve_context_from_api(
                t_name, t_type, coordinates, res_funcs
            )
            total_get_context_time += t.seconds_from_start
        with Timer() as t:
            model_url = os.environ.get("LLAMA_URL")
            model_connector = LanguageModelCreator.create_llm_connector(
                model_url, accessibility_sys_prompt
            )
            llm_res = model_connector.generate(question, context)
            total_model_time += t.seconds_from_start
        if correct_function in res_funcs:
            correct_function_choice += 1
        correct_answer = re.findall(r"\d+,\d+|\d+\.\d+|\d+", correct_answer)
        numbers_from_response = re.findall(
            r"\d+,\d+|\d+\.\d+|\d+", llm_res.split("ОТВЕТ")[1]
        )
        correct_answer = list(map(lambda x: x.replace(",", "."), correct_answer))
        numbers_from_response = list(
            map(lambda x: x.replace(",", "."), numbers_from_response)
        )
        correct_answer = list(map(float, correct_answer))
        numbers_from_response = list(map(float, numbers_from_response))
        if (
            all(elem in correct_answer for elem in numbers_from_response)
            and numbers_from_response
        ):
            correct_accessibility_answer += 1
        print(f"Function to call: {res_funcs}")
        print(f"Context from tables: {context}")
        print(f"Answer from LLM: {llm_res}")
        print(f"Correct numbers: {correct_answer}")
        print(f"Numbers from LLM answer: {numbers_from_response}")
        print(f"Number of correct answers: {correct_accessibility_answer}")

    corr_func_percent = round(correct_function_choice / total_access_questions * 100, 2)
    corr_answer_percent = round(
        correct_accessibility_answer / total_access_questions * 100, 2
    )
    avg_func_choose_time = round(total_function_choose_time / total_access_questions, 2)
    avg_func_check_time = round(total_check_function_time / total_access_questions, 2)
    avg_get_context_time = round(total_get_context_time / total_access_questions, 2)
    avg_model_time = round(total_model_time / total_access_questions, 2)

    with open(path_to_results, "w") as f:
        print(
            f"""Total accessibility samples: {total_access_questions}
Percentage of correctly chosen functions: {corr_func_percent}
Percentage of correct accessibility answers: {corr_answer_percent}
Average function choosing time (accessibility): {avg_func_choose_time}
Average functions checking time (accessibility): {avg_func_check_time}
Average getting context from API time (accessibility): {avg_get_context_time}
Average answer generation time: {avg_model_time}""",
            file=f,
        )


def strategy_pipeline_test(metrics_to_calculate: List, chunk_num: int = 4) -> None:
    """Tests strategy pipeline.

    Evaluate metrics for model answers using 'deepeval' and measures elapsed
    time for context retrieving and final answer generation.
    Writes results to .txt file at the specified path.

    Args:
        metrics_to_calculate: list of metrics to be calculated
        chunk_num: number of chunks to be extracted from vector storage
    Returns: None
    """
    print("Strategy pipeline test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "strategy_pipeline_test_results.txt"
    )
    path_to_metrics = Path(
        path_to_data, "test_results", "strategy_pipeline_metrics_results.csv"
    )
    os.makedirs(os.path.dirname(path_to_results), exist_ok=True)

    metrics_result = {
        "question": [],
        "correct_answer": [],
        "llm_ans": [],
        "context": [],
    }
    for metric in metrics_to_calculate:
        metrics_result[f"{metric.__name__}_score"] = []
        metrics_result[f"{metric.__name__}_reason"] = []

    total_chroma_time = 0
    total_model_time = 0

    for i, row in strategy_data.iterrows():
        question = row["question"]
        correct_answer = row["correct_answer"]
        print(f"Processing question {i}")
        with Timer() as t:
            context = retrieve_context_from_chroma(question, collection_name, chunk_num)
            total_chroma_time += t.seconds_from_start
        with Timer() as t:
            model_url = os.environ.get("LLAMA_URL")
            context = context.replace('"', "'")
            model_connector = LanguageModelCreator.create_llm_connector(
                model_url, strategy_sys_prompt
            )
            llm_ans = model_connector.generate(question, context)
            total_model_time += t.seconds_from_start
        metrics_result["question"].append(question)
        metrics_result["correct_answer"].append(correct_answer)
        metrics_result["llm_ans"].append(llm_ans)
        metrics_result["context"].append(context)
        test_case = LLMTestCase(
            input=question,
            actual_output=llm_ans,
            expected_output=correct_answer,
            retrieval_context=[context],
        )
        for metric in metrics_to_calculate:
            try:
                metric.measure(test_case)
                metrics_result[f"{metric.__name__}_score"].append(metric.score)
                metrics_result[f"{metric.__name__}_reason"].append(metric.reason)
            except Exception as e:
                metrics_result[f"{metric.__name__}_score"].append("-1")
                metrics_result[f"{metric.__name__}_reason"].append(
                    type(e).__name__ + " - " + str(e)
                )
                continue
    metrics_result_df = pd.DataFrame.from_dict(metrics_result)
    metrics_score_columns = list(
        filter(lambda x: "score" in x, metrics_result_df.columns.tolist())
    )
    metrics_to_print = []
    for column in metrics_score_columns:
        avg_score = metrics_result_df[metrics_result_df[column] != -1][column].mean()
        success_metric = metrics_result_df[metrics_result_df[column] != -1].shape[0]
        metrics_to_print.append(
            f"Average {column} is {avg_score}. Number of successfully"
            f" processed questions {success_metric}"
        )
    short_metrics_result = "\n".join(metrics_to_print)
    metrics_result_df.to_csv(path_to_metrics, index=False)

    avg_get_context_time = round(total_chroma_time / total_strategy_questions, 2)
    avg_model_time = round(total_model_time / total_strategy_questions, 2)

    with open(path_to_results, "w") as f:
        print(
            f"""Total strategy samples: {total_strategy_questions}
Average getting context from ChromaDB time (strategy): {avg_get_context_time}
Average answer generation time (strategy): {avg_model_time}
Short metrics results:
{short_metrics_result}""",
            file=f,
        )


if __name__ == "__main__":
    chunks = 4
    metrics = [answer_relevancy, faithfulness, correctness_metric]
    # choose_pipeline_test()
    # choose_functions_test()
    # accessibility_pipeline_test()
    strategy_pipeline_test(metrics, chunks)
