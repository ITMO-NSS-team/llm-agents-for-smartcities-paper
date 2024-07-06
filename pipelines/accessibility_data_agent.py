import json
import requests
import csv
import api.summary_tables_requests
from pprint import pprint
from typing import Dict, List
from tools.accessibility_tools import *



tools = [get_general_stats_education_tool,
         get_general_stats_healthcare_tool,
         get_general_stats_culture_tool,
         get_general_stats_sports_tool,
         get_general_stats_services_tool]

def get_relevant_api_function_from_llm(model_url: str, tools: Dict, question: str) -> str:
    params = {
      # "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          # "content": "You are a smart AI assistant, You have high expertise in the field of "
          #            "urbanistics and structure of Saint Petersburg. "
          "content": f"You are a helpful assistant with access to the following functions. "
                     f"Use them if required - {str(tools)}."
        },
        {
          "role": "user",
          # "content": f"You have access to a database with several tables that contain statistics for different types "
          #            f"of territories. Please choose a function to extract information that is needed to answer the "
          #            f"following question: {question}\n"
          #            f"Extra information: {extra_data}"
          "content": f"Extract all relevant data for answering this question: {question}\n"
                     f"Please only return the function call with parameters."
        }
      ]
    }

    response = requests.post(url=model_url, json=params)
    res = json.loads(response.text)

    # pprint(res)
    # pprint(type(res['choices'][0]['message']['content']))
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
                all_questions += 1
                print(question)
                print(dataset)
                print(res_funcs)
                print('____________________________________')
        print(f'All processed questions: {all_questions}')
        print(f'Questions with correct answers: {correct_answers}')

def service_accessibility_pipeline(question: str, coordinates: List, t_type: str) -> str:
    # add extra logic
    res_funcs = []
    if t_type == "city":
        res_funcs.append('get_general_stats_city')
    elif t_type == "mo" or t_type == "district":
        res_funcs.append('get_general_stats_districts_mo')
    elif t_type == "block":
        res_funcs.append('get_general_stats_block')
    # send request to agent llm
    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    llm_res = get_relevant_api_function_from_llm(model_url, tools, question)
    llm_res_funcs = parse_function_names_from_llm_answer(llm_res)
    res_funcs = res_funcs + llm_res_funcs
    if not res_funcs:
        res_funcs.append('get_general_stats_city')

    # call function
    input_data = {"coordinates": coordinates, "type": "Polygon"}
    context = ''
    for func in res_funcs:
        cur_handle = getattr(api.summary_tables_requests, func)
        context += str(cur_handle(input_data))

    # prep data for main call
    # send request to 70b and parse answer
    # return answer
    pass


if __name__ == "__main__":
    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    # model_url = 'http://10.32.2.2:8671/v1/chat/completions'  # Meta-Llama-3-70B-Instruct-v2.Q4_K_S

    test_data_file = '/Users/lizzy/Downloads/accessibility_questions.csv'

    # get_metrics(model_url, test_data_file, tools)
    test_coord = {
        "coordinates": [
          [
            [30.2679419, 60.1126515], [30.2679786, 60.112752], [30.2682489, 60.1127275], [30.2682122, 60.112627], [30.2679419, 60.1126515]
          ]
        ],
        "type": "Polygon"
    }
    func_handle = getattr(api.summary_tables_requests, 'get_general_stats_city')
    r = func_handle(test_coord)
    pprint(r)
