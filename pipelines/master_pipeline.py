import json
import requests
import csv
from typing import Dict, List


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


def get_relevant_function_from_llm(model_url: str, tools: Dict, question: str, extra_data: str) -> str:
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
                           f"{question}\n Extra information: {extra_data}"
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


def parse_function_names_from_llm_answer(llm_res: str) -> List:
    res = []
    if 'service_accessibility_pipeline' in llm_res:
        res.append('api')
    if 'strategy_development_pipeline' in llm_res:
        res.append('rag')
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


# model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
model_url = 'http://10.32.2.2:8671/v1/chat/completions'  # Meta-Llama-3-70B-Instruct-v2.Q4_K_S

extra_data = 'Coordinates: {"type": "polygon", "coords": [[[30.688828198781902, 59.775976109763285]]]}, territory type: city.'

test_data_file = './test_data/access_and_strategy_questions.csv'

get_metrics(model_url, test_data_file, tools, extra_data)
