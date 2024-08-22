import csv
import json
import re
from typing import Dict, List

from new_web_api import NewWebAssistant
import requests

from models.prompts.strategy_prompt import strategy_sys_prompt


tools = [
    {
        "name": "service_accessibility_pipeline",
        "description": "This pipeline returns detailed information about the accessibility of various urban "
        "services and facilities. It evaluates the accessibility of healthcare, population, "
        "housing facilities, recreation, playgrounds, education (schools, universities, etc.), "
        "public transport, churches and temples, sports infrastructure  (stadiums, etc.), "
        "cultural and leisure facilities (theatres, circuses, zoos, etc.), and more. "
        "The input usually contain words such as 'доступность', 'обеспеченность', 'доля', 'количество',  "
        "'средняя доступность', 'среднее время', 'общая площадь', 'численность', etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "dict",
                }
            },
            "required": ["coordinates"],
        },
    },
    {
        "name": "strategy_development_pipeline",
        "description": "This pipeline provides answers to questions based on the development strategy "
        "document. It uses Retrieval-Augmented Generation (RAG) to extract relevant "
        "information from the provided document. The tool is designed to answer strategic "
        "questions about urban development, including healthcare, education, infrastructure, "
        "and other aspects covered in the development strategy. The input usually contain words "
        "such as 'планируемый', 'меры', etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                }
            },
            "required": ["question"],
        },
    },
]


def get_relevant_function_from_llm(
    model_url: str, tools: Dict, question: str, extra_data: str
) -> str:
    params = {
        "messages": [
            {
                "role": "system",
                "content": f"You are a helpful assistant with access to the following functions. "
                f"Use them if required - {str(tools)}.",
            },
            {
                "role": "user",
                "content": f"Extract all relevant data for answering this question: "
                f"{question}\n Extra information: {extra_data}."
                f"You MUST return ONLY the function name. "
                # f"You MUST return ONLY the function call with parameters. "
                f"Do NOT return any other additional text.",
            },
        ]
    }

    response = requests.post(url=model_url, json=params)
    res = json.loads(response.text)

    # pprint(res)
    # pprint(type(res['choices'][0]['message']['content']))
    return res["choices"][0]["message"]["content"]


def parse_function_names_from_llm_answer(llm_res: str) -> List:
    match = re.search(r"^\[Correct answer\]:.*", llm_res, re.MULTILINE)
    res = []
    if match:
        correct_answer_line = match.group(0)
        if "service_accessibility_pipeline" in correct_answer_line:
            res.append("api")
        if "strategy_development_pipeline" in correct_answer_line:
            res.append("rag")
    return res


def check_choice_correctness(question: str, answer: str, tools: List):
    sys_prompt = (
        "You are a knowledgeable, efficient, and direct AI assistant. Provide concise answers, "
        "focusing on the key information needed. Offer suggestions tactfully when appropriate to "
        "improve outcomes. Engage in productive collaboration with the user."
    )
    model = NewWebAssistant()
    model.set_sys_prompt(sys_prompt)
    user_message = (
        f"[Instruction]: You are given question, descriptions of 2 functions and an answer from another "
        f"Llama model, which has chosen one of these functions. Your task is to compare "
        f"the chosen function with the question and the descriptions and determine "
        f"if the function was selected correctly. If the chosen function is correct, "
        f"return the function name. If the function is selected incorrectly, return the name "
        f"of another function.\n"
        f"[Question]: {question}.\n"
        f"[Answer]: {answer}.\n"
        f"[Function Descriptions]: {tools}.\n"
        f"[Task]: "
        f"Compare the chosen function with the function descriptions and the question "
        f"to determine if the function was selected correctly. Return the name of correct function in this format: "
        f"[Correct answer]: correct function."
    )
    ans = model(user_message, as_json=False)

    return ans


def get_metrics(
    model_url: str, test_data_file: str, tools: List, extra_data: str
) -> None:
    all_questions = 0
    correct_answers = 0
    incorrect_answers = []
    with open(test_data_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row["question"]
            dataset = row["source"]
            if dataset != "":
                llm_res_to_check = get_relevant_function_from_llm(
                    model_url, tools, question, extra_data
                )
                llm_res = check_choice_correctness(
                    question, llm_res_to_check, tools
                )
                res_funcs = parse_function_names_from_llm_answer(llm_res)
                if dataset in res_funcs:
                    correct_answers += 1
                else:
                    incorrect_answers.append([question, dataset, res_funcs])
                all_questions += 1
                print(question)
                print(dataset)
                print(res_funcs)
                print("____________________________________")
        print(f"All processed questions: {all_questions}")
        print(f"Questions with correct answers: {correct_answers}")
        print("Incorrect answers:")
        for answer in incorrect_answers:
            print(answer)
        print(f"Accuracy: {correct_answers / all_questions}")


if __name__ == "__main__":
    sys_prompt = strategy_sys_prompt

    model_url = "http://10.32.2.2:8673/v1/chat/completions"  # meta-llama3-8b-q8-function-calling

    extra_data = 'Coordinates: {"type": "polygon", "coords": [[[30.688828198781902, 59.775976109763285]]]}, territory type: city.'

    # File with 10 questions for testing
    # test_data_file = './test_data/test_access_and_strategy_questions.csv'

    test_data_file = "./test_data/access_and_strategy_questions.csv"

    get_metrics(model_url, test_data_file, tools, extra_data)
