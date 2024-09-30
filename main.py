import logging

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipelines.master_pipeline import answer_question_with_llm
from utils.get_logs import filter_records
from utils.get_logs import get_records_by_id
from utils.logging_config import configure_logging


class Question(BaseModel):
    question_body: str = (
        "What are the demographic development problems of Saint Petersburg?"
    )
    chunk_num: int = 4
    territory_name_id: str = "Saint Petersburg"
    territory_type: str = "city"
    selection_zone: list = [
        [
            [30.2679419, 60.1126515],
            [30.2679786, 60.112752],
            [30.2682489, 60.1127275],
            [30.2682122, 60.112627],
            [30.2679419, 60.1126515],
        ]
    ]


app = FastAPI(on_startup=[configure_logging])

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

logger = logging.getLogger(__name__)


@app.post("/question")
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
    logger.info(f"Query: {question.question_body}")
    logger.info(f"Number of chunks: {question.chunk_num}")
    logger.info(f"Territory name: {question.territory_name_id}")
    logger.info(f"Territory type: {question.territory_type}")
    logger.info(f"Selected zone: {question.selection_zone}")
    llm_res = answer_question_with_llm(
        question.question_body,
        question.selection_zone,
        question.territory_type,
        question.territory_name_id,
        question.chunk_num,
    )
    cid = correlation_id.get()
    request_logs = filter_records(get_records_by_id(cid))
    return {"llm_res": llm_res, "request_logs": request_logs}


@app.get("/build_test")
async def build_test():
    """Endpoint for build test

    Returns:
        dict: message - just an indicator
    """
    return {"message": "App is running"}
