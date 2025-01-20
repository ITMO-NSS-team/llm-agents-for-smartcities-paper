from pathlib import Path
from typing import Any, List
from uuid import uuid4

from deepeval.metrics import BaseMetric
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase
from deepeval.test_case import LLMTestCaseParams
import joblib
import pandas as pd

from modules.models.vsegpt_api import VseGPTConnector
from modules.variables.definitions import ROOT
from utils.measure_time import Timer


def get_answer_and_evaluate(
    dataset: pd.DataFrame,
    metrics: List[BaseMetric],
    model: Any,
    system_prompt: str,
    save_path: Path,
):
    model_name = model
    model = VseGPTConnector(model=model, sys_prompt=system_prompt)

    metrics_result = {
        "question": [],
        "correct_answer": [],
        "llm_ans": [],
        "answer_generation_time": [],
    }
    for metric in metrics:
        metrics_result[f"{metric.__name__}_score"] = []
        metrics_result[f"{metric.__name__}_reason"] = []

    for i, row in dataset.iterrows():
        print(f"Processing question {i}")
        question = row["question"]
        correct_answer = row["correct_answer"]
        context = row["territory_name"]
        try:
            with Timer() as t:
                if context:
                    ans = model.generate(f"{question} Выбранная территория: {context}.")
                else:
                    ans = model.generate(question)
            metrics_result["answer_generation_time"].append(t.seconds_from_start)
        except Exception as e:
            print(e)
            ans = None

        metrics_result["question"].append(question)
        metrics_result["correct_answer"].append(correct_answer)
        metrics_result["llm_ans"].append(ans)

        if ans:
            test_case = LLMTestCase(
                input=question,
                actual_output=ans,
                expected_output=correct_answer,
            )

            for metric in metrics:
                try:
                    metric.measure(test_case)
                    metrics_result[f"{metric.__name__}_score"].append(metric.score)
                    metrics_result[f"{metric.__name__}_reason"].append(metric.reason)
                except Exception as e:
                    metrics_result[f"{metric.__name__}_score"].append(None)
                    metrics_result[f"{metric.__name__}_reason"].append(
                        type(e).__name__ + " - " + str(e)
                    )
                    continue
        else:
            metrics_result[f"{metric.__name__}_score"].append(None)
            metrics_result[f"{metric.__name__}_reason"].append(None)

    # Save to file
    Path(save_path).mkdir(parents=True, exist_ok=True)
    res_pth = Path(save_path / f"{model_name.split('/')[1]}_{str(uuid4())[:8]}.csv")
    metrics_result = pd.DataFrame.from_dict(metrics_result)
    metrics_result.to_csv(res_pth)
    print(f"Results were saved into {res_pth}")

    # Calc mean values
    print(f"Number of questions: {metrics_result.shape[0]}")
    print(f'Processed questions: {metrics_result["llm_ans"].count()}')
    for metric in metrics:
        print(
            f"""Number of valid metrics:
              {metrics_result[f"{metric.__name__}_score"].count()}"""
        )
        print(
            f"""Average {metric.__name__} value for {model_name}:
             {metrics_result[f"{metric.__name__}_score"].mean()}"""
        )
    print(f"Average answer time: {metrics_result['answer_generation_time'].mean()}\n")

    return metrics_result


if __name__ == "__main__":
    system_prompt = """You are a smart AI assistant. You have high expertise in the field
of city building, urbanistics and structure of Saint-Petersburg.
Answer the question following the rules below.
1. Before giving an answer to the user question, provide an
explanation. Mark the answer with keyword ’ANSWER’, and
explanation with ’EXPLANATION’. Both answer and explanation must be
in the English language. 
2. If the question is about complaints, answer about at least 5 
complaints topics. 
3. Answer should be five sentences maximum. 
4. In answers you must use only the English language.
"""

    models_list = [
        # "openai/gpt-4o-2024-08-06",
        # "mistralai/mixtral-8x22b-instruct",
        # "meta-llama/llama-3.1-70b-instruct",
        "llama-3.1-70b-instruct-int4",
    ]
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
            "1. Correctness and Relevance:"
            "- Compare the actual response against the expected response. Determine the"
            " extent to which the actual response captures the key elements and concepts of"
            " the expected response."
            "- Assign higher scores to actual responses that accurately reflect the core"
            " information of the expected response, even if only partial."
            "2. Numerical Accuracy and Interpretation:"
            "- Pay particular attention to any numerical values present in the expected"
            " response. Verify that these values are correctly included in the actual"
            " response and accurately interpreted within the context."
            "- Ensure that units of measurement, scales, and numerical relationships are"
            " preserved and correctly conveyed."
            "3. Allowance for Partial Information:"
            "- Do not heavily penalize the actual response for incompleteness if it covers"
            " significant aspects of the expected response. Prioritize the correctness of"
            " provided information over total completeness."
            "4. Handling of Extraneous Information:"
            "- While additional information not present in the expected response should not"
            " necessarily reduce score, ensure that such additions do not introduce"
            " inaccuracies or deviate from the context of the expected response."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        **metrics_init_params,
    )

    pth = Path(ROOT, "data", "preprocessed_questions (1).xlsx")
    save_path = Path(ROOT / "pipelines/tests/metrics_results")
    dataset = pd.read_excel(pth)
    dataset = dataset[dataset["correct_answer"].notnull()]
    dataset = dataset.reindex(index=dataset.index[::])
    res = joblib.Parallel(n_jobs=1, prefer="threads")(
        joblib.delayed(get_answer_and_evaluate)(
            dataset, [correctness_metric], m, system_prompt, save_path
        )
        for m in models_list
    )
