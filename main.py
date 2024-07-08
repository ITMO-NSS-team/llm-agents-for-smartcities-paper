from fastapi import FastAPI
import logging
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pipelines.master_pipeline import answer_question_with_llm


class Question(BaseModel):
    question_body: str = 'Какие проблемы демографического развития Санкт-Петербурга?'
    chunk_num: int = 4
    territory_name_id: str = 'Санкт-Петербург'
    territory_type: str = 'city'
    selection_zone: list = [
        [
            [30.2679419, 60.1126515], [30.2679786, 60.112752], [30.2682489, 60.1127275],
            [30.2682122, 60.112627], [30.2679419, 60.1126515]
        ]
    ]


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/question')
async def read_item(question: Question):
    """Get a response for a given question using a RAG pipeline with a vector DB and LLM.

    Args:
        question_body (str): a question from the user (natural language, no additional prompts)
        chunk_num (int): number of chunks that will be returned by the DB and used as a context
        territory_name_id (str): name of the territory
        territory_type (str): type of the territory
        selection_zone (list): coordinates of the territory

    Returns:
        dict: llm_res - pipeline's answer to the user's question
    """
    logging.basicConfig(level=logging.INFO)
    logging.info(f'main: question: {question.question_body}')
    logging.info(f'main: chunk_num: {question.chunk_num}')
    logging.info(f'main: territory_name_id: {question.territory_name_id}')
    logging.info(f'main: territory_type: {question.territory_type}')
    logging.info(f'main: selection_zone: {question.selection_zone}')
    llm_res = answer_question_with_llm(question.question_body, question.selection_zone,
                                       question.territory_type, question.territory_name_id,
                                       question.chunk_num)
    return {'llm_res': llm_res}
