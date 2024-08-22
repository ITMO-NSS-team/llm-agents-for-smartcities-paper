import logging
import os

import chroma_rag.loading as chroma_connector
from models.new_web_api import NewWebAssistant
from models.prompts.strategy_prompt import strategy_sys_prompt


logger = logging.getLogger(__name__)


def retrieve_context_from_chroma(q: str, collect_name: str, c_num: int) -> str:
    res = chroma_connector.chroma_view(q, collect_name, c_num)
    context = ""
    context_list = []
    metadata = []
    for ind, chunk in enumerate(res):
        context = f"{context}Отрывок {ind}: {chunk[0].page_content} "
        context_list.append(chunk[0].page_content)
        metadata.append(
            (
                chunk[0].metadata["chapter"],
                os.path.basename(chunk[0].metadata["source"]),
            )
        )
    logger.info(f"Chunk metadata from ChromaDB: {metadata}")
    return context


def generate_answer(q: str, s_p: str, c: str) -> str:
    model = NewWebAssistant()
    model.set_sys_prompt(s_p)
    model.add_context(c)
    response = model(q, as_json=True)
    return response


def strategy_development_pipeline(
    question: str,
    chunk_num: int = 4,
) -> str:
    collection_name = "strategy-spb"
    logger.info(f"Chroma collection name: {collection_name}")
    logger.info(f"Question: {question}")
    logger.info(f"Chunks num: {chunk_num}")
    # Get context from ChromaDB
    context = retrieve_context_from_chroma(
        question, collection_name, chunk_num
    )
    # Get question answer from Llama
    response = generate_answer(question, strategy_sys_prompt, context)

    return response


if __name__ == "__main__":
    question = "Какие проблемы демографического развития Санкт-Петербурга?"
    print(strategy_development_pipeline(question))
