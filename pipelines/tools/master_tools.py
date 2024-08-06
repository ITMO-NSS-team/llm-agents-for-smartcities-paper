tools = [
    {
        "name": "service_accessibility_pipeline",
        "description": "This pipeline returns detailed information about the accessibility of various urban "
                       "services and facilities and their number. It evaluates the accessibility of healthcare, population, "
                       "housing facilities, recreation, playgrounds, education (schools, universities, etc.), "
                       "public transport, churches and temples, sports infrastructure  (stadiums, etc.), "
                       "cultural and leisure facilities (theatres, circuses, zoos, etc.), and more. "
                       "It can also return information about the dissatisfaction of the population and information on various complaints. "
                       "The input usually contain words such as 'доступность', 'обеспеченность', 'доля', 'количество', "
                       "'средняя доступность', 'среднее время', 'общая площадь', 'численность', 'сколько' etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "dict",
                }
            },
            "required": ["coordinates"]
        }
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
            "required": ["question"]
        }
    }
]