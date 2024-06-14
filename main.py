from fastapi import FastAPI
from pydantic import BaseModel

import chroma_rag.loading as chroma_connector
from models.web_api import WebAssistant
from models.standard_prompt import standard_sys_prompt


class Question(BaseModel):
    question_body: str = 'Какие проблемы демографического развития Санкт-Петербурга?'
    chunk_num: int = 3
    territory_name_id: str = 'Санкт-Петербург'
    territory_type: str = 'city'
    user_selection_zone: list = [
      [
        [
          30.184679, 59.954721
        ],
        [
          30.184727, 59.954813
        ]
      ]
    ]


app = FastAPI()

@app.post('/question')
async def read_item(question: Question):
    """Get a response for a given question using a RAG pipeline with a vector DB and LLM.

    Args:
        question_body (str): a question from the user (natural language, no additional prompts)
        chunk_num (int): number of chunks that will be returned by the DB and used as a context
        territory_name_id (str): name of the territory
        territory_type (str): type of the territory
        user_selection_zone (list): coordinates of the territory

    Returns:
        dict: llm_res - pipeline's answer to the user's question, context_list - context returned by DB
    """
    collection_name = 'strategy-spb'
    res = chroma_connector.chroma_view(question.question_body, collection_name, question.chunk_num)
    context = ''
    context_list = []
    for ind, chunk in enumerate(res):
        context = f'{context}Отрывок {ind}: {chunk[0].page_content} '
        context_list.append(chunk[0].page_content)

    # model = WebAssistant()
    # model.set_sys_prompt(standard_sys_prompt)
    # model.add_context(context)
    # llm_res = model(question.question_body, as_json=True)
    return {'llm_res': res[0][0].page_content, 'context_list': context_list}
