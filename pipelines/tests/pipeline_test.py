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

from models.definitions import ROOT
from models.prompts.strategy_prompt import accessibility_sys_prompt
from models.prompts.strategy_prompt import strategy_sys_prompt
from models.vsegpt_api import VseGPTConnector
from pipelines.accessibility_data_agent import choose_functions
from pipelines.accessibility_data_agent import generate_answer
from pipelines.accessibility_data_agent import retrieve_context_from_api
from pipelines.master_pipeline import check_pipeline
from pipelines.master_pipeline import choose_pipeline
from pipelines.strategy_pipeline import retrieve_context_from_chroma
from utils.measure_time import Timer


path_to_data = Path(ROOT, "pipelines", "tests")
strategy_and_access_data = pd.read_csv(
    Path(path_to_data, "test_data", "questions_for_test.csv")
)
strategy_data = pd.read_csv(
    Path(path_to_data, "test_data", "strategy_questions.csv")
)
access_data = pd.read_csv(
    Path(path_to_data, "test_data", "access_questions.csv")
)
collection_name = "strategy-spb"
total_all_questions = strategy_and_access_data.shape[0]
total_strategy_questions = strategy_data.shape[0]
total_access_questions = access_data.shape[0]

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
    # criteria="Correctness - determine if the actual output is correct according to the expected output.",  # more strictly evaluate consistency with the correct answer
    criteria="Correctness - determine if the actual output is factually correct according to the expected output.",
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
    **metrics_init_params,
)


def choose_pipeline_test() -> None:
    """Tests pipeline choosing functions.

    Counts number of correctly chosen pipelines and measures elapsed time for choosing and checking results.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print("Pipeline choosing test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "pipeline_choose_test_results.txt"
    )

    total_correct_pipeline = 0
    total_choose_time = 0
    total_check_time = 0

    for i, row in strategy_and_access_data.iterrows():
        question = row["question"]
        correct_pipeline = row["correct_pipeline"]
        print(f"Processing question {i}")
        with Timer() as t:
            raw_pipeline = choose_pipeline(question)
            total_choose_time += t.seconds_from_start
        with Timer() as t:
            checked_pipeline = check_pipeline(question, raw_pipeline)
            total_check_time += t.seconds_from_start
        if checked_pipeline[0] == correct_pipeline:
            total_correct_pipeline += 1

    corr_pipe_percent = round(
        total_correct_pipeline / total_all_questions * 100, 2
    )
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

    Counts number of correctly chosen function and measures elapsed time for choosing and checking results.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print("API functions choosing test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "choose_functions_test_results.txt"
    )

    total_correct_functions = 0
    total_time = 0

    for i, row in access_data.iterrows():
        question = row["question"]
        correct_functions = row["correct_functions"]
        print(f"Processing question {i}")
        with Timer() as t:
            functions = choose_functions(question)
            total_time += t.seconds_from_start
        if functions[0] == correct_functions:
            total_correct_functions += 1

    corr_func_percent = round(
        total_correct_functions / total_access_questions * 100, 2
    )
    avg_func_choose_time = round(total_time / total_access_questions, 2)

    with open(path_to_results, "w") as f:
        print(
            f"""Percentage of correctly chosen functions: {corr_func_percent}
Average function choosing time: {avg_func_choose_time}""",
            file=f,
        )


def accessibility_pipeline_test(
    coordinates: list, t_type: str, t_id: str
) -> None:
    """Tests whole accessibility pipeline.

    Counts number of correctly chosen function and correct answers, measures elapsed time for choosing and checking
    and final answer generation.
    Writes results to .txt file at the specified path.

    Args:
        coordinates: nested list of coordinates of specific area
        t_type: the type of territory that was 'selected' on the map
        t_id: the name of 'selected' territory

    Returns: None
    """
    print("Accessibility pipeline test is running...")
    path_to_results = Path(
        path_to_data, "test_results", "accessibility_pipeline_test_results.txt"
    )

    correct_function_choice = 0
    correct_accessibility_answer = 0
    total_model_time = 0
    total_function_choose_time = 0
    total_get_context_time = 0

    for i, row in access_data.iterrows():
        question = row["question"]
        correct_answer = row["correct_answer"]
        correct_functions = row["correct_functions"]
        print(f"Processing question {i}")
        with Timer() as t:
            functions = choose_functions(question)
            total_function_choose_time += t.seconds_from_start
        with Timer() as t:
            context = retrieve_context_from_api(coordinates, functions)
            total_get_context_time += t.seconds_from_start
        with Timer() as t:
            llm_res = generate_answer(
                question, accessibility_sys_prompt, context
            )
            total_model_time += t.seconds_from_start
        if correct_functions in functions:
            correct_function_choice += 1
        correct_answer = re.findall(r"\d+,\d+|\d+\.\d+|\d+", correct_answer)
        numbers_from_response: List[str] = re.findall(
            r"\d+,\d+|\d+\.\d+|\d+", llm_res
        )
        if (
            all(elem in [correct_answer] for elem in numbers_from_response)
            and numbers_from_response
        ):
            correct_accessibility_answer += 1

    corr_func_percent = round(
        correct_function_choice / total_access_questions * 100, 2
    )
    corr_answer_percent = round(
        correct_accessibility_answer / total_access_questions * 100, 2
    )
    avg_func_choose_time = round(
        total_function_choose_time / total_access_questions, 2
    )
    avg_get_context_time = round(
        total_get_context_time / total_access_questions, 2
    )
    avg_model_time = round(total_model_time / total_access_questions, 2)

    with open(path_to_results, "w") as f:
        print(
            f"""Total accessibility samples: {total_access_questions}
Percentage of correctly chosen functions: {corr_func_percent}
Percentage of correct accessibility answers: {corr_answer_percent}
Average function choosing time (accessibility): {avg_func_choose_time}
Average getting context from API time (accessibility): {avg_get_context_time}
Average answer generation time: {avg_model_time}""",
            file=f,
        )


def strategy_pipeline_test(
    metrics_to_calculate: List, chunk_num: int = 4
) -> None:
    """Tests strategy pipeline.

    Evaluate metrics for model answers using 'deepeval' and measures elapsed time for context retrieving and final
    answer generation.
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
            context = retrieve_context_from_chroma(
                question, collection_name, chunk_num
            )
            total_chroma_time += t.seconds_from_start
        with Timer() as t:
            llm_ans = generate_answer(question, strategy_sys_prompt, context)
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
                metrics_result[f"{metric.__name__}_reason"].append(
                    metric.reason
                )
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
        avg_score = metrics_result_df[metrics_result_df[column] != -1][
            column
        ].mean()
        success_metric = metrics_result_df[
            metrics_result_df[column] != -1
        ].shape[0]
        metrics_to_print.append(
            f"Average {column} is {avg_score}. Number of successfully processed questions {success_metric}"
        )
    short_metrics_result = "\n".join(metrics_to_print)
    metrics_result_df.to_csv(path_to_metrics, index=False)

    avg_get_context_time = round(
        total_chroma_time / total_strategy_questions, 2
    )
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
    coords = [
        [
            [30.2679419, 60.1126515],
            [30.2679786, 60.112752],
            [30.2682489, 60.1127275],
            [30.2682122, 60.112627],
            [30.2679419, 60.1126515],
        ]
    ]
    ttype = ""
    tid = ""
    metrics = [answer_relevancy, faithfulness, correctness_metric]
    # choose_pipeline_test()
    # choose_functions_test()
    # accessibility_pipeline_test(coords, ttype, tid)
    # strategy_pipeline_test(metrics, chunks)
