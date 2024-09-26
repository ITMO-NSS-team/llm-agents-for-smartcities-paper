import datetime
from pathlib import Path
from typing import Tuple

from pipeline_test import path_to_data


base_path_to_results = Path(path_to_data, "test_results")


def generate_path_to_results(
    test_name: str, model_name: str, check_flag: bool = False
) -> Tuple[Path, Path]:
    test_datetime = str(datetime.datetime.now().replace(second=0, microsecond=0))
    if not check_flag:
        short_results_path = Path(
            base_path_to_results,
            test_name,
            f"{test_name}_results_{model_name}_{test_datetime}.txt",
        )
        full_results_path = Path(
            base_path_to_results,
            test_name,
            f"{test_name}_{model_name}_{test_datetime}.csv",
        )
        return short_results_path, full_results_path
    else:
        short_results_path = Path(
            base_path_to_results,
            test_name,
            f"{test_name}_with_check_results_{model_name}_{test_datetime}.txt",
        )
        full_results_path = Path(
            base_path_to_results,
            test_name,
            f"{test_name}_with_check_{model_name}_{test_datetime}.csv",
        )
        return short_results_path, full_results_path
