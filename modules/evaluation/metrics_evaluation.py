import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import pandas as pd

from modules.variables.definitions import ArrayLike


def evaluate_on_predictions(
    question: ArrayLike,
    answers: ArrayLike,
    targets: ArrayLike,
    metrics: List[BaseMetric],
    context: ArrayLike | None = None,
    retrieval_context: ArrayLike | None = None,
    answer_time: ArrayLike | None = None,
    metrics_config: Dict | None = None,
    model_name: str | None = None,
    **kwargs,
) -> Tuple[pd.DataFrame, Dict]:
    """Function for LLM's answers evaluation with given set of metrics.

    This function takes answers from LLM, correct answers, actual question,
    and other supplementary data, required by metrics to evaluate model's performance.

    Args:
        question (ArrayLike): Questions to be answered by the model. Must be presented as
        List, pandas's Series, or numpy's ndarray.
        answers (ArrayLike): Answers given by the model. Must be presented as
        List, pandas's Series, or numpy's ndarray.
        targets (ArrayLike): Expected answer to be given.  Must be presented as
        List, pandas's Series, or numpy's ndarray.
        metrics (List[BaseMetric]): List of metrics to be calculated.
        context (ArrayLike | None, optional): Additional information, which can be used by
        the model to give an answer to the question. Must be presented as
        List, pandas's Series, or numpy's ndarray. Defaults to None.
        retrieval_context (ArrayLike | None, optional): Additional information, which
        represents RAG pipeline's retireval results. Defaults to None.
        answer_time (ArrayLike | None, optional): Optional parameter, time taken by the
        model to give an answer. If specified, in the end will be calculated average time
        performance of the model. Defaults to None.
        metrics_config (Dict | None, optional): Optional parameter. Config with parameters
        for metrics. Defaults to None. Currently is not being used.
        model_name (str | None, optional): Optional parameter. Model's name which
        will be used for metrics evaluation.
        Defaults to None. Currently is not being used.

    Returns:
        Tuple: Dataframe with metrics results, question, llm answers and rest data,
        that were passed to the function. Second returned object is a dictionary with
        average metrics result and mean time performance, if time performance was
        specified.
    """
    content = {
        "input": question,
        "actual_output": answers,
        "expected_output": targets,
        "context": context,
        "retrieval_context": retrieval_context,
        "answer_time": answer_time,
    }

    metrics_dict = {f"{m.__name__}": "" for m in metrics}
    content = pd.DataFrame.from_dict(content | metrics_dict)

    for i, row in content.iterrows():
        test_case = LLMTestCase(
            input=row["input"],
            actual_output=row["actual_output"],
            expected_output=row["expected_output"],
            context=row["context"],
            retrieval_context=row["retrieval_context"],
        )
        for m in metrics:
            result = m.measure(test_case)
            row[f"{m.__name__}"] = result

    means = {f"{m.__name__}": content[f"{m.__name__}"].mean() for m in metrics}
    if answer_time is not None:
        means["average_answer_time"] = content["answer_time"].mean()
    if kwargs.get("save_path") is not None:
        content.to_csv(
            Path(kwargs["save_path"], f"metrics_results_{datetime.datetime.now()}.csv")
        )
        with open(
            Path(
                kwargs["save_path"],
                f"additional_metrics_results_{datetime.datetime.now()}.txt",
            ),
            "w",
        ) as pth:
            print(means, file=pth)
        print(f'Results were saved into: \n\t{kwargs["save_path"]}')

    return content, means
