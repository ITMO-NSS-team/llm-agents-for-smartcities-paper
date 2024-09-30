from pipelines.accessibility_pipeline import service_accessibility_pipeline
from pipelines.master_pipeline import answer_question_with_llm
from pipelines.strategy_pipeline import strategy_development_pipeline


def test_strategy_development_pipeline():
    question = "What are the demographic development problems of Saint Petersburg?"
    answer = strategy_development_pipeline(question)
    print(f"\nStrategy development pipeline\nQuestion: {question}\nAnswer: {answer}\n")
    assert answer != ""


def test_service_accessibility_pipeline():
    question = "What is the average accessibility time of hospitals and schools?"
    territory_type = "city"
    territory_name = "Saint Petersburg"
    territory_coords = None
    answer = service_accessibility_pipeline(
        question, territory_coords, territory_type, territory_name
    )
    print(f"\nService accessibility pipeline\nQuestion: {question}\nAnswer: {answer}\n")
    assert answer != ""


def test_master_pipeline():
    question = "What are the demographic development problems of Saint Petersburg?"
    chunk_num = 4
    territory_type = "city"
    territory_name = "Saint Petersburg"
    territory_coords = None
    answer = answer_question_with_llm(
        question, territory_coords, territory_type, territory_name, chunk_num
    )
    print(f"\nMaster pipeline\nQuestion: {question}\nAnswer: {answer}\n")
    assert answer != ""

    question = "What is the average accessibility time of hospitals and schools?"
    answer = answer_question_with_llm(
        question, territory_coords, territory_type, territory_name, chunk_num
    )
    print(f"\nMaster pipeline\nQuestion: {question}\nAnswer: {answer}\n")
    assert answer != ""
