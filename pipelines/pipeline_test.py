from typing import List, Callable
import re
import csv


def accessibility_pipeline_accuracy(path_to_questions: str,
                                    func: Callable[[str], str]):
    """
    Prints simple accuracy score for batch of questions

    Args:
        path_to_questions: Path to file with test questions and answers
        func: Main pipeline function applied partially with 3 arguments
    """
    all_questions: int = 0
    correct_answers: int = 0
    with open(path_to_questions, newline='', mode='r') as f:
        csv_file = csv.reader(f)
        for lines in csv_file:
            if lines[0] == 'Вопрос':
                continue
            query: str = lines[0]
            all_questions += 1
            response = func(query)
            answer: List[str] = [s.replace(',', '.') for s in re.findall(r"\d+,\d+|\d+\.\d+|\d+", lines[1])]
            numbers_from_response: List[str] = re.findall(r"\d+,\d+|\d+\.\d+|\d+", response)
            if all(elem in answer for elem in numbers_from_response):
                correct_answers += 1
    print('Percentage of correct answers: ', round(correct_answers / all_questions * 100, 2))
