import re
import pandas as pd
from typing import List

from pipelines.master_pipeline import choose_pipeline, check_pipeline
from pipelines.accessibility_data_agent import choose_functions, retrieve_context_from_api, generate_answer
from pipelines.strategy_pipeline import retrieve_context_from_chroma
from models.prompts.strategy_prompt import accessibility_sys_prompt, strategy_sys_prompt
from utils.measure_time import Timer


strategy_and_access_data = pd.read_csv('test_data/questions_for_test.csv')
strategy_data = pd.read_csv('test_data/strategy_questions.csv')
access_data = pd.read_csv('test_data/access_questions.csv')
collection_name = 'strategy-spb'
total_all_questions = strategy_and_access_data.shape[0]
total_strategy_questions = strategy_data.shape[0]
total_access_questions = access_data.shape[0]


def choose_pipeline_test() -> None:
    """ Tests pipeline choosing functions.

    Counts number of correctly chosen pipelines and measures elapsed time for choosing and checking results.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print('Pipeline choosing test is running...')
    path_to_results = 'test_results/pipeline_choose_test_results.txt'

    total_correct_pipeline = 0
    total_choose_time = 0
    total_check_time = 0

    for i, row in strategy_and_access_data.iterrows():
        question = row['question']
        correct_pipeline = row['correct_pipeline']
        print(f'Processing question {i}')
        with Timer() as t:
            raw_pipeline = choose_pipeline(question)
            total_choose_time += t.seconds_from_start
        with Timer() as t:
            checked_pipeline = check_pipeline(question, raw_pipeline)
            total_check_time += t.seconds_from_start
        if checked_pipeline[0] == correct_pipeline:
            total_correct_pipeline += 1

    corr_pipe_percent = round(total_correct_pipeline / total_all_questions * 100, 2)
    avg_pipe_choose_time = round(total_choose_time / total_all_questions, 2)
    avg_pipe_check_time = round(total_check_time / total_all_questions, 2)

    with open(path_to_results, 'w') as f:
        print(f'''Percentage of correctly chosen pipeline: {corr_pipe_percent}
Average pipeline choosing time: {avg_pipe_choose_time}
Average pipeline check time: {avg_pipe_check_time}''', file=f)


def choose_functions_test() -> None:
    """ Tests API functions choosing function.

    Counts number of correctly chosen function and measures elapsed time for choosing and checking results.
    Writes results to .txt file at the specified path.

    Returns: None
    """
    print('API functions choosing test is running...')
    path_to_results = 'test_results/choose_functions_test_results.txt'

    total_correct_functions = 0
    total_time = 0

    for i, row in access_data.iterrows():
        question = row['question']
        correct_functions = row['correct_functions']
        print(f'Processing question {i}')
        with Timer() as t:
            functions = choose_functions(question)
            total_time += t.seconds_from_start
        if functions[0] == correct_functions:
            total_correct_functions += 1

    corr_func_percent = round(total_correct_functions / total_access_questions * 100, 2)
    avg_func_choose_time = round(total_time / total_access_questions, 2)

    with open(path_to_results, 'w') as f:
        print(f'''Percentage of correctly chosen functions: {corr_func_percent}
Average function choosing time: {avg_func_choose_time}''', file=f)


def accessibility_pipeline_test(coordinates: list,
                                t_type: str,
                                t_id: str) -> None:
    """ Tests whole accessibility pipeline.

    Counts number of correctly chosen function and correct answers, measures elapsed time for choosing and checking
    and final answer generation.
    Writes results to .txt file at the specified path.

    Args:
        coordinates: nested list of coordinates of specific area
        t_type: the type of territory that was 'selected' on the map
        t_id: the name of 'selected' territory

    Returns: None
    """
    print('Accessibility pipeline test is running...')
    path_to_results = 'test_results/accessibility_pipeline_test_results.txt'

    correct_function_choice = 0
    correct_accessibility_answer = 0
    total_model_time = 0
    total_function_choose_time = 0
    total_get_context_time = 0

    for i, row in access_data.iterrows():
        question = row['question']
        correct_answer = row['correct_answer']
        correct_functions = row['correct_functions']
        print(f'Processing question {i}')
        with Timer() as t:
            functions = choose_functions(question)
            total_function_choose_time += t.seconds_from_start
        with Timer() as t:
            context = retrieve_context_from_api(coordinates, functions)
            total_get_context_time += t.seconds_from_start
        with Timer() as t:
            llm_res = generate_answer(question, accessibility_sys_prompt, context)
            total_model_time += t.seconds_from_start
        if correct_functions in functions:
            correct_function_choice += 1
        correct_answer = re.findall(r"\d+,\d+|\d+\.\d+|\d+", correct_answer)
        numbers_from_response: List[str] = re.findall(r"\d+,\d+|\d+\.\d+|\d+", llm_res)
        if all(elem in [correct_answer] for elem in numbers_from_response) and numbers_from_response:
            correct_accessibility_answer += 1

    corr_func_percent = round(correct_function_choice / total_access_questions * 100, 2)
    corr_answer_percent = round(correct_accessibility_answer / total_access_questions * 100, 2)
    avg_func_choose_time = round(total_function_choose_time / total_access_questions, 2)
    avg_get_context_time = round(total_get_context_time / total_access_questions, 2)
    avg_model_time = round(total_model_time / total_access_questions, 2)

    with open(path_to_results, 'w') as f:
        print(f'''Total accessibility samples: {total_access_questions}
Percentage of correctly chosen functions: {corr_func_percent}
Percentage of correct accessibility answers: {corr_answer_percent}
Average function choosing time (accessibility): {avg_func_choose_time}
Average getting context from API time (accessibility): {avg_get_context_time}
Average answer generation time: {avg_model_time}''', file=f)


def strategy_pipeline_test(chunk_num: int = 4) -> None:
    """ Tests strategy pipeline.

    Evaluate metrics for model answers using 'deepeval' and measures elapsed time for context retrieving and final
    answer generation.
    Writes results to .txt file at the specified path.

    Args:
        chunk_num: number of chunks to be extracted from vector storage

    Returns: None
    """
    print('Strategy pipeline test is running...')
    path_to_results = 'test_results/strategy_pipeline_test_results.txt'

    total_chroma_time = 0
    total_model_time = 0

    for i, row in strategy_data.iterrows():
        question = row['question']
        # correct_answer = row['correct_answer']
        print(f'Processing question {i}')
        with Timer() as t:
            context = retrieve_context_from_chroma(question, collection_name, chunk_num)
            total_chroma_time += t.seconds_from_start
        with Timer() as t:
            answer = generate_answer(question, strategy_sys_prompt, context)
            total_model_time += t.seconds_from_start
        # Possible to add deepeval metrics calculation here

    avg_get_context_time = round(total_chroma_time / total_strategy_questions, 2)
    avg_model_time = round(total_model_time / total_strategy_questions, 2)

    with open(path_to_results, 'w') as f:
        print(f'''Total strategy samples: {total_strategy_questions}
Average getting context from ChromaDB time (strategy): {avg_get_context_time}
Average answer generation time (strategy): {avg_model_time}''', file=f)


if __name__ == '__main__':
    chunks = 4
    coords = [
        [
            [30.2679419, 60.1126515], [30.2679786, 60.112752], [30.2682489, 60.1127275],
            [30.2682122, 60.112627], [30.2679419, 60.1126515]
        ]
    ]
    ttype = ''
    tid = ''
    # choose_pipeline_test()
    # choose_functions_test()
    # accessibility_pipeline_test(coords, ttype, tid)
    strategy_pipeline_test(chunks)
