import logging
import chroma_rag.loading as chroma_connector
from models.new_web_api import NewWebAssistant
from models.prompts.buildings_prompt import buildings_sys_prompt
from models.prompts.strategy_prompt import strategy_sys_prompt_new


logging.basicConfig(level=logging.INFO)


def strategy_development_pipeline(question: str, chunk_num: int = 4) -> str:
    collection_name = 'strategy-spb'
    logging.info(f'Strategy RAG: Chroma collection name: {collection_name}')
    logging.info(f'Strategy RAG: Question: {question}')
    logging.info(f'Strategy RAG: Chunks num: {chunk_num}')
    # Get context from ChromaDB
    res = chroma_connector.chroma_view(question, collection_name, chunk_num)
    context = ''
    context_list = []
    for ind, chunk in enumerate(res):
        context = f'{context}Отрывок {ind}: {chunk[0].page_content} '
        context_list.append(chunk[0].page_content)
    logging.info(f'Strategy RAG: Context: {context_list}')
    # Get question answer from Llama
    model = NewWebAssistant()
    model.set_sys_prompt(strategy_sys_prompt_new)
    model.add_context(context)
    response = model(question, as_json=True)
    logging.info(f'Strategy RAG: Final answer: {response}')
    return response


if __name__ == "__main__":
    question = 'Какие проблемы демографического развития Санкт-Петербурга?'
    print(strategy_development_pipeline(question))
