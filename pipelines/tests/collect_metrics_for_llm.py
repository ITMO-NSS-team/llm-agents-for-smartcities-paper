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
        """1. Correctness and Relevance:
- Compare the actual response against the expected response. 
Determine the extent to which the actual response 
captures the key elements and concepts of the expected response. 
- Assign higher scores to actual responses that accurately reflect 
the core information of the expected response, even if only partial 
2. Numerical Accuracy and Interpretation:
- Pay particular attention to any numerical values present 
in the expected response. Verify that these values are 
correctly included in the actual response and accurately 
interpreted within the context. 
- Ensure that units of measurement, scales, and numerical 
relationships are preserved and correctly conveyed. 
3. Allowance for Partial Information: 
- Do not heavily penalize the actual response for incompleteness 
if it covers significant aspects of the expected response. 
Prioritize the correctness of provided information over 
total completeness. 
4. Handling of Extraneous Information: 
- While additional information not present in the expected response 
should not necessarily reduce score, 
ensure that such additions do not introduce inaccuracies 
or deviate from the context of the expected response."""
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
