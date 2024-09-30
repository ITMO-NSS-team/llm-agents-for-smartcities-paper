import logging
import os

import chroma_rag.loading as chroma_connector
from modules.models.connector_creator import LanguageModelCreator
from modules.variables.prompts import strategy_sys_prompt
from utils.measure_time import Timer


logger = logging.getLogger(__name__)


def retrieve_context_from_chroma(q: str, collect_name: str, c_num: int) -> str:
    """Retrieves the given number of chunks from ChromaDB based on the user question."""
    res = chroma_connector.chroma_view(q, collect_name, c_num)
    context = ""
    context_list = []
    metadata = []
    for ind, chunk in enumerate(res):
        context = f"{context}Chunk {ind}: {chunk[0].page_content} "
        context_list.append(chunk[0].page_content)
        metadata.append(
            (
                chunk[0].metadata["chapter"],
                os.path.basename(chunk[0].metadata["source"]),
            )
        )
    logger.info(f"Chunk metadata from ChromaDB: {metadata}")
    return context


def strategy_development_pipeline(
    question: str,
    chunk_num: int = 4,
) -> str:
    """Pipeline designed to handle strategy development data.
    Extracts the context from ChromaDB and passes it to the LLM to answer the question.

    Args:
        question: A question from the user.
        chunk_num: Number of chunks that will be returned by the DB.

    Returns: Answer to the question.
    """
    collection_name = "strategy-spb"
    logger.info(f"Chroma collection name: {collection_name}")
    logger.info(f"Chunks num: {chunk_num}")
    # Get context from ChromaDB
    with Timer() as t:
        context = retrieve_context_from_chroma(question, collection_name, chunk_num)
        logger.info(f"Retrieve context time: {t.seconds_from_start} sec")
    # Get question answer from model
    model_url = os.environ.get("LLAMA_URL")
    model_connector = LanguageModelCreator.create_llm_connector(
        model_url, strategy_sys_prompt
    )
    with Timer() as t:
        response = model_connector.generate(question, context)
        logger.info(f"Answer generation time: {t.seconds_from_start} sec")

    return response
