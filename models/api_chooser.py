import json
import re

from web_api import WebAssistant
from new_web_api import NewWebAssistant
from models.prompts.strategy_prompt import strategy_sys_prompt
from pprint import pprint

import json
import requests
import csv
from typing import Dict, List
from models.model import UrbAssistant

tools = [
    {
        "name": "EndpointsListings.cities",
        "description": "Retrieve a list of cities. Can filter to show only centers.",
        "parameters": {
            "type": "object",
            "properties": {
                "centers_only": {
                    "type": "boolean"
                }
            },
            "required": []
        }
    }
    ,
    {
        "name": "EndpointsListings.cities_statistics",
        "description": "Retrieve statistics for cities.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "EndpointsListings.city_service_type_living_situations",
        "description": "Retrieve living situations for a specific city service type.",
        "parameters": {
            "type": "object",
            "properties": {
                "city_service_type_id": {
                    "type": "string"
                }
            },
            "required": ["city_service_type_id"]
        }
    },
    {
        "name": "EndpointsListings.city_service_types",
        "description": "Retrieve a list of city service types.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "EndpointsCity.municipalities",
        "description": "Retrieve municipalities for a specific city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "centers_only": {
                    "type": "boolean"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "EndpointsCity.districts",
        "description": "Retrieve administrative units (districts) for a specific city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "centers_only": {
                    "type": "boolean"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "EndpointsCity.territories",
        "description": "Retrieve territories for a specific city, accepting city code or city name in Russian.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "centers_only": {
                    "type": "boolean"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "EndpointsCity.houses",
        "description": "Retrieve houses for a specific city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "geometryAsCenter": {
                    "type": "boolean"
                },
                "livingOnly": {
                    "type": "boolean"
                },
                "requiredProperties": {
                    "type": "array"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "EndpointsCity.blocks",
        "description": "Retrieve blocks for a specific city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "centers_only": {
                    "type": "boolean"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "EndpointsMetrics.blocks_accessibility",
        "description": "Retrieve accessibility information for specific blocks within a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "block_id": {
                    "type": "string"
                }
            },
            "required": ["city", "block_id"]
        }
    }
    ,
    {
        "name": "EndpointsProvision.get_provision",
        "description": "Post endpoint to retrieve provision information based on various parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "service_types": {
                    "type": "array"
                },
                "year": {
                    "type": "integer"
                },
                "calculation_type": {
                    "type": "string"
                },
                "user_selection_zone": {
                    "type": "string"
                },
                "valuation_type": {
                    "type": "string"
                },
                "service_impotancy": {
                    "type": "string"
                }
            },
            "required": ["city", "service_types", "year", "calculation_type", "user_selection_zone", "valuation_type",
                         "service_impotancy"]
        }
    }
    ,
    {
        "name": "EndpointsSummaryTables.get_summary_table",
        "description": "Post endpoint to retrieve summary tables based on geographical context.",
        "parameters": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string"
                },
                "territory_name_id": {
                    "type": "string"
                },
                "territory_type": {
                    "type": "string"
                },
                "selection_zone": {
                    "type": "string"
                }
            },
            "required": ["table", "territory_name_id", "territory_type", "selection_zone"]
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
                           f"{question}\n Extra information: {extra_data}."
                           f"You MUST return ONLY the function name. "
                # f"You MUST return ONLY the function call with parameters. "
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
    match = re.search(r'^\[Correct answer\]:.*', llm_res, re.MULTILINE)
    res = []
    if match:
        correct_answer_line = match.group(0)
        for tool in tools:
            if tool['name'] in correct_answer_line:
                res.append(tool['name'])
    return res


def check_choice_correctness(question: str, answer: str, tools: List):
    sys_prompt = "You are a knowledgeable, efficient, and direct AI assistant. Provide concise answers, " \
                 "focusing on the key information needed. Offer suggestions tactfully when appropriate to " \
                 "improve outcomes. Engage in productive collaboration with the user."
    model = NewWebAssistant()
    model.set_sys_prompt(sys_prompt)
    user_message = f"[Instruction]: You are given question, descriptions of 2 functions and an answer from another " \
                   f"Llama model, which has chosen one of these functions. Your task is to compare " \
                   f"the chosen function with the question and the descriptions and determine " \
                   f"if the function was selected correctly. If the chosen function is correct, " \
                   f"return the function name. If the function is selected incorrectly, return the name " \
                   f"of another function.\n" \
                   f"[Question]: {question}.\n" \
                   f"[Answer]: {answer}.\n" \
                   f"[Function Descriptions]: {tools}.\n" \
                   f"[Task]: " \
                   f"Compare the chosen function with the function descriptions and the question " \
                   f"to determine if the function was selected correctly. Return the name of correct function in this format: " \
                   f"[Correct answer]: correct function."
    ans = model(user_message, as_json=False)

    return ans


def get_metrics(model_url: str, test_data_file: str, tools: List, extra_data: str) -> None:
    all_questions = 0
    correct_answers = 0
    incorrect_answers = []
    with open(test_data_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row['question']
            dataset = row['source']
            if dataset != '':
                llm_res_to_check = get_relevant_function_from_llm(model_url, tools, question, extra_data)
                llm_res = check_choice_correctness(question, llm_res_to_check, tools)
                res_funcs = parse_function_names_from_llm_answer(llm_res)
                if dataset in res_funcs:
                    correct_answers += 1
                else:
                    incorrect_answers.append([question, dataset, res_funcs])
                all_questions += 1
                print(question)
                print(dataset)
                print(res_funcs)
                print('____________________________________')
        print(f'All processed questions: {all_questions}')
        print(f'Questions with correct answers: {correct_answers}')
        print(f'Incorrect answers:')
        for answer in incorrect_answers:
            print(answer)
        print(f'Accuracy: {correct_answers / all_questions}')


if __name__ == "__main__":
    sys_prompt = strategy_sys_prompt

    model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling

    extra_data = ('Coordinates: {"type": "polygon", "coords": [[[30.688828198781902, 59.775976109763285]]]}, '
                  'territory type: city.')

    # File with 10 questions for testing
    # test_data_file = './test_data/test_access_and_strategy_questions.csv'

    test_data_file = './test_data/access_and_strategy_questions.csv'

    get_metrics(model_url, test_data_file, tools, extra_data)
