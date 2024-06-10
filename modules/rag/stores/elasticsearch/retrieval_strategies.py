from typing import Union

from langchain_elasticsearch._utilities import DistanceStrategy
from langchain_elasticsearch.vectorstores import BaseRetrievalStrategy

from rag.utilities import settings


class BM25RetrievalStrategy(BaseRetrievalStrategy):
    """BM25 retrieval strategy for ElasticSearch"""

    def index(
            self,
            dims_length: Union[int, None],
            vector_query_field: str,
            similarity: Union[DistanceStrategy, None],
    ) -> dict:
        index_kwargs = {"settings": settings.es_index_settings,
                        "mappings": settings.es_index_mappings}
        return index_kwargs

    def query(
            self,
            query_vector: Union[list[float], None],
            query: Union[str, None],
            *,
            k: int,
            fetch_k: int,
            vector_query_field: str,
            text_field: str,
            filter: list[dict],
            similarity: Union[DistanceStrategy, None],
    ) -> dict:
        if query is None:
            raise ValueError(
                "You must provide a query to perform a similarity search."
            )
        new_query = dict(settings.es_query_template)
        new_query['multi_match']['query'] = query
        query_body = {'query': new_query}
        return query_body

    def require_inference(self) -> bool:
        return False
