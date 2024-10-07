from pathlib import Path

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
import pandas as pd

from modules.evaluation.metrics_evaluation import evaluate_on_predictions
from modules.models.vsegpt_api import VseGPTConnector
from modules.variables import ROOT


path_to_answers = Path(
    ROOT,
    "pipelines",
    "tests",
    "metrics_results",
    "llama-3.1-70b-instruct_6119026c.csv",
)
answers_dataset = pd.read_csv(path_to_answers)

metric_model = VseGPTConnector(model="openai/gpt-4o-mini", sys_prompt="")
metrics_init_params = {
    "model": metric_model,
    "verbose_mode": False,
    "async_mode": False,
    "strict_mode": False,
}

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

metrics, additional_res = evaluate_on_predictions(
    question=answers_dataset["question"],
    answers=answers_dataset["llm_ans"],
    targets=answers_dataset["correct_answer"],
    metrics=[correctness_metric],
    save_path=path_to_answers.parent,
)
