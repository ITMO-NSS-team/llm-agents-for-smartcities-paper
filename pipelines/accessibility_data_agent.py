import csv
import logging
import re
from typing import Dict, List
from tools.accessibility_tools_rus import *

import api.summary_tables_requests
from models.new_web_api import *
from models.prompts.strategy_prompt import *
from pipelines.tools.accessibility_tools_rus import *


logging.basicConfig(level=logging.INFO)

tools = [get_general_stats_education_tool,
         get_general_stats_healthcare_tool,
         get_general_stats_culture_tool,
         get_general_stats_sports_tool,
         get_general_stats_services_tool]


def get_relevant_api_function_from_llm(model_url: str, tools: Dict, question: str) -> str:
    params = {
        "messages": [
            {
                "role": "system",
                "content": f"You are a helpful assistant with access to the following functions. "
                           f"Use them if required - {str(tools)}."
            },
            {
                "role": "user",
                "content": f"Extract all relevant data for answering this question: {question}\n"
                           f"Please only return the function call with parameters."
            }
        ]
    }
    response = requests.post(url=model_url, json=params)
    res = json.loads(response.text)
    return res['choices'][0]['message']['content']


def parse_function_names_from_llm_answer(llm_res: str) -> List:
    res = []
    functions = ['get_general_stats_city',
                 'get_general_stats_districts_mo',
                 'get_general_stats_block',
                 'get_general_stats_education',
                 'get_general_stats_healthcare',
                 'get_general_stats_culture',
                 'get_general_stats_sports',
                 'get_general_stats_services']
    for api_func in functions:
        if api_func in llm_res:
            res.append(api_func)
    return res


def get_metrics(model_url: str, test_data_file: str, tools: List):
    all_questions = 0
    correct_answers = 0
    with open(test_data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row['question']
            dataset = row['dataset']
            if dataset != '':
                llm_res = get_relevant_api_function_from_llm(model_url, tools, question)
                res_funcs = parse_function_names_from_llm_answer(llm_res)
                if dataset in res_funcs:
                    correct_answers += 1
                else:
                    print(question)
                    print(dataset)
                    print(res_funcs)
                    print('____________________________________')
                all_questions += 1

        print(f'All processed questions: {all_questions}')
        print(f'Questions with correct answers: {correct_answers}')


def service_accessibility_pipeline(question: str, coordinates: List, t_type: str, t_id: str) -> str:
    # If territory type is specified, make sure to include the function for that type
    res_funcs = []
    if t_type == "city":
        res_funcs.append('get_general_stats_city')
    elif t_type == "municipality" or t_type == "district":
        res_funcs.append('get_general_stats_districts_mo')
    elif t_type is None and t_id is not None:
        res_funcs.append('get_general_stats_block')

    # Send request to agent llm
    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    llm_res = get_relevant_api_function_from_llm(model_url, tools, question)
    llm_res_funcs = parse_function_names_from_llm_answer(llm_res)
    res_funcs = res_funcs + llm_res_funcs
    if not res_funcs:
        res_funcs.append('get_general_stats_city')
    logging.info(f'Accessibility agent: Functions list: {res_funcs}')

    # Call functions and get context
    input_data = {"coordinates": coordinates, "type": "Polygon"}
    context = ''
    try:
        for func in res_funcs:
            cur_handle = getattr(api.summary_tables_requests, func)
            context += str(cur_handle(input_data))
    except ValueError as e:
        logging.error(f'Accessibility agent: Could NOT retrieve context from API: {e}')

    logging.info(f'Accessibility agent: Context: {context}')

    # Send request to Llama 70B and parse final answer
    model = NewWebAssistant()
    model.set_sys_prompt(strategy_sys_prompt)
    model.add_context(context)
    response = model(question, as_json=True)
    logging.info(f'Accessibility agent: Final answer: {response}')
    return response

def read_json_file(filename):
    with open(filename) as f:
        context = json.load(f)
    return context
def run_pipeline_on_local_data(question: str, table: str):
    input_data = {
        'get_general_stats_city': read_json_file(
            './test_data/summary_tables/get_general_stats_city.json'),
        'get_general_stats_districts_mo': read_json_file(
            './test_data/summary_tables/get_general_stats_districts_mo.json'),
        'get_general_stats_block': read_json_file(
            './test_data/summary_tables/get_general_stats_block.json'),
        'get_general_stats_education': read_json_file(
            './test_data/summary_tables/get_general_stats_education.json'),
        'get_general_stats_healthcare': read_json_file(
            './test_data/summary_tables/get_general_stats_healthcare.json'),
        # 'get_general_stats_culture': json.loads(
        #   './test_data/summary_tables/get_general_stats_culture.json'),
        'get_general_stats_sports': read_json_file(
            './test_data/summary_tables/get_general_stats_sports.json'),
        'get_general_stats_services': read_json_file(
            './test_data/summary_tables/get_general_stats_services.json')}

    res_funcs = []
    if table == "Общий контекст – общая таблица сводка по городу":
        res_funcs.append('get_general_stats_city')
    elif table == "Территориальный контекст – сводка по выбранному району или МО":
        res_funcs.append('get_general_stats_districts_mo')
    elif table == "Территориальный контекст – сводка по выбранному кварталу":
        res_funcs.append('get_general_stats_block')

    # Send request to agent llm
    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    llm_res = get_relevant_api_function_from_llm(model_url, tools, question)
    llm_res_funcs = parse_function_names_from_llm_answer(llm_res)
    res_funcs = res_funcs + llm_res_funcs
    if not res_funcs:
        res_funcs.append('get_general_stats_city')
    logging.info(f'Accessibility agent: Functions list: {res_funcs}')
    if 'get_general_stats_culture' in res_funcs:
        res_funcs.remove('get_general_stats_culture')

    context = ''
    for func in res_funcs:
        context += str(input_data[func])
    logging.info(f'Accessibility agent: Context: {context}')

    # Send request to Llama 70B and parse final answer
    model = NewWebAssistant()
    model.set_sys_prompt(strategy_sys_prompt)
    model.add_context(context)
    response = model(question, as_json=True)
    logging.info(f'Accessibility agent: Final answer: {response}')
    return response


def run_test_full_pipeline_with_local_data():
    import time

    start = time.time()
    end = time.time()
    print(end - start)
    test_data = './test_data/urb_accessibility_questions.csv'

    all_questions: int = 0
    correct_answers: int = 0
    full_time = 0
    with open(test_data, 'r') as f:
        csv_file = csv.reader(f)
        for lines in csv_file:
            if lines[0] == 'Вопрос':
                continue
            question = lines[0]
            print(question)
            print(f'correct answer: {lines[1]}')
            table_name = lines[2]
            all_questions += 1
            beg = time.time()
            response = run_pipeline_on_local_data(question, table_name)
            full_time += time.time() - beg
            print(f'llm answer: {response}')
            correct_answer = re.findall(r"\d+\,\d+|\d+\.\d+|\d+", lines[1])
            short_correct_answer = correct_answer[0].replace(',', '.')
            print(f'short correct answer: {short_correct_answer}')
            if short_correct_answer in response:
                correct_answers += 1
            print(f'all: {all_questions}')
            print(f'correct: {correct_answers}')
            print('___________________________')
    print('Percentage of correct answers: ', round(correct_answers / all_questions * 100, 2))
    print(f'Average time: {full_time/all_questions}')
    print(f'Full time: {full_time}')



if __name__ == "__main__":
    # Check how well the agent can identify the correct function for the job
    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    # model_url = 'http://10.32.2.2:8671/v1/chat/completions'  # Meta-Llama-3-70B-Instruct-v2.Q4_K_S

    # test_data_file = 'test_data/accessibility_questions.csv'
    # get_metrics(model_url, test_data_file, tools)

    # # Test the pipeline on one question
    # question = 'Каково среднее время доступности школ?'
    # coords = [
    #     [
    #         [30.2679419, 60.1126515], [30.2679786, 60.112752], [30.2682489, 60.1127275], [30.2682122, 60.112627],
    #         [30.2679419, 60.1126515]
    #     ]
    # ]
    # ttype = 'city'
    # t_id = 'saint-petersburg'
    # service_accessibility_pipeline(question, coords, ttype, t_id)

    # Test the whole pipeline on data from files (instead of api)
    run_test_full_pipeline_with_local_data()
