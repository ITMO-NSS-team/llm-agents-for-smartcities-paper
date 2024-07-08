import csv
import json
import logging
import requests
from typing import Dict, List

from models.prompts.strategy_prompt import *
from models.new_web_api import *
from pipelines.accessibility_data_agent import service_accessibility_pipeline
from pipelines.strategy_pipeline import strategy_development_pipeline
import pipelines


tools = [
    {
        "name": "service_accessibility_pipeline",
        "description": "This pipeline returns detailed information about the accessibility of various urban "
                       "services and facilities. It evaluates the accessibility of healthcare, population, "
                       "housing facilities, recreation, playgrounds, education, public transport, churches "
                       "and temples, sports infrastructure, cultural and leisure facilities, and more. "
                       "The tool takes geographical coordinates as input and provides comprehensive statistics "
                       "for the specified area.",
        "parameters": {
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "dict",
                }
            },
            "required": ["coordinates"]
        }
    },
    {
        "name": "strategy_development_pipeline",
        "description": "This pipeline provides answers to questions based on the development strategy "
                       "document. It uses Retrieval-Augmented Generation (RAG) to extract relevant "
                       "information from the provided document. The tool is designed to answer strategic "
                       "questions about urban development, including healthcare, education, infrastructure, "
                       "and other aspects covered in the development strategy. The user must provide the question.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                }
            },
            "required": ["question"]
        }
    }
]


def get_relevant_function_from_llm(model_url: str, tools: Dict, question: str) -> str:
    params = {
        "messages": [
            {
                "role": "system",
                "content": f"You are a helpful assistant with access to the following functions. "
                           f"Use them if required - {str(tools)}."
            },
            {
                "role": "user",
                "content": f"Extract all relevant data for answering this question: "
                           f"{question}\n"
                           f"You MUST return ONLY the function call with parameters. "
                           f"Do NOT return any other additional text."
            }
        ]
    }

    response = requests.post(url=model_url, json=params)
    res = json.loads(response.text)

    # pprint(res)
    # pprint(type(res['choices'][0]['message']['content']))
    return res['choices'][0]['message']['content']


def parse_function_names_from_llm_answer_for_metrics(llm_res: str) -> List:
    res = []
    if 'service_accessibility_pipeline' in llm_res:
        res.append('api')
    if 'strategy_development_pipeline' in llm_res:
        res.append('rag')
    return res


def parse_function_names_from_llm_answer(llm_res: str) -> List:
    res = []
    functions = ['service_accessibility_pipeline',
                 'strategy_development_pipeline']
    for pipeline_func in functions:
        if pipeline_func in llm_res:
            res.append(pipeline_func)
    return res


def get_metrics(model_url: str, test_data_file: str, tools: List, extra_data: str) -> None:
    all_questions = 0
    correct_answers = 0
    with open(test_data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row['question']
            dataset = row['source']
            if dataset != '':
                llm_res = get_relevant_function_from_llm(model_url, tools, question, extra_data)
                res_funcs = parse_function_names_from_llm_answer_for_metrics(llm_res)
                if dataset in res_funcs:
                    correct_answers += 1
                all_questions += 1
                print(question)
                print(dataset)
                print(res_funcs)
                print('____________________________________')
        print(f'All processed questions: {all_questions}')
        print(f'Questions with correct answers: {correct_answers}')


def answer_question_with_llm(question: str, coordinates: List, t_type: str, t_id: str,  chunk_num: int) -> str:
    # add loading tools later
    # Send request to agent llm
    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    llm_res = get_relevant_function_from_llm(model_url, tools, question)
    res_funcs = parse_function_names_from_llm_answer(llm_res)
    if not res_funcs:
        res_funcs.append('strategy_development_pipeline')
    logging.info(f'Master pipeline: Functions list: {res_funcs}')

    # Call function -> just the first one TODO: think how to handle multiple replies from llm
    if res_funcs[0] == 'strategy_development_pipeline':
        fun_handle = getattr(pipelines.strategy_pipeline, 'strategy_development_pipeline')
        llm_res = str(fun_handle(question, chunk_num))
    elif res_funcs[0] == 'service_accessibility_pipeline':
        fun_handle = getattr(pipelines.accessibility_data_agent, 'service_accessibility_pipeline')
        llm_res = str(fun_handle(question, coordinates, t_type, t_id))
    logging.info(f'Master pipeline: Final answer: {llm_res}')
    return llm_res


if __name__ == "__main__":
    # model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
    # # model_url = 'http://10.32.2.2:8671/v1/chat/completions'  # Meta-Llama-3-70B-Instruct-v2.Q4_K_S
    # test_data_file = './test_data/access_and_strategy_questions.csv'
    # get_metrics(model_url, test_data_file, tools, extra_data)

    question = 'Какие проблемы демографического развития Санкт-Петербурга?'
    chunk_num = 4
    print(answer_question_with_llm(question, None, None, chunk_num))
