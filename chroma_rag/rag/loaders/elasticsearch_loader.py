from typing import Optional, Any, Iterator, Callable

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_elasticsearch import ElasticsearchStore

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

from rag.loaders.utilities import get_text, es_query_all_hits


class ElasticsearchLoader(BaseLoader):
    def __init__(self,
                 index_name: str,
                 es_connection: Optional[Elasticsearch] = None,
                 es_url: Optional[str] = None,
                 es_user: Optional[str] = None,
                 es_password: Optional[str] = None,
                 es_params: Optional[dict[str, Any]] = None,
                 content_key: Optional[str] = None,
                 metadata_func: Optional[Callable[[dict, dict], dict]] = None,
                 scroll: str = "5m",
                 raise_on_error: bool = True,
                 preserve_order: bool = False,
                 size: int = 1000,
                 request_timeout: Optional[float] = None,
                 clear_scroll: bool = True
                 ):
        self.index_name = index_name
        self._content_key = content_key
        self._metadata_func = metadata_func
        self._scroll = scroll
        self._raise_on_error = raise_on_error
        self._preserve_order = preserve_order
        self._size = size
        self._request_timeout = request_timeout
        self._clear_scroll = clear_scroll

        if es_connection is not None:
            self.client = es_connection
        elif es_url is not None:
            self.client = ElasticsearchStore.connect_to_elasticsearch(
                es_url=es_url,
                username=es_user,
                password=es_password,
                es_params=es_params,
            )
        else:
            raise ValueError(
                """Either provide a pre-existing Elasticsearch connection, \
                or valid credentials for creating a new connection."""
            )

    def lazy_load(self) -> Iterator[Document]:
        """Load and return documents from the Elasticsearch."""
        validate = True
        for hit in scan(self.client, query=es_query_all_hits, index=self.index_name,
                        scroll=self._scroll, raise_on_error=self._raise_on_error,
                        preserve_order=self._preserve_order, size=self._size,
                        request_timeout=self._request_timeout, clear_scroll=self._clear_scroll):
            yield self._parse(hit, validate)
            validate = False

    def _parse(self, hit: dict[str, Any], validate: bool = True) -> Document:
        """Convert given hit to document."""
        if validate and self._content_key is not None:
            self._validate_content_key(hit['_source'])
        if validate and self._metadata_func is not None:
            self._validate_metadata_func(hit)

        text = self._get_text(hit['_source'])
        metadata = self._get_metadata(hit, id=hit['_id'])
        return Document(page_content=text, metadata=metadata)

    def _get_text(self, source: dict[str, Any]) -> str:
        """Convert source to string format"""
        if self._content_key is not None:
            content = source.get(self._content_key)
        else:
            content = source

        return get_text(content)

    def _get_metadata(self, hit: dict[str, Any], **additional_fields: Any) -> dict[str, Any]:
        """Return a metadata dictionary base on the existence of metadata_func."""
        if self._metadata_func is not None:
            return self._metadata_func(hit, additional_fields)
        return additional_fields

    def _validate_content_key(self, source: dict[str, Any]) -> None:
        """Check if a content key is valid"""
        if source.get(self._content_key) is None:
            raise ValueError(
                f"Expected the schema of Elasticsearch hit's source \
                    with the key `{self._content_key}` with the not-none value"
            )

    def _validate_metadata_func(self, hit: dict[str, Any]) -> None:
        """Check if the metadata_func output is valid"""
        if self._metadata_func is not None:
            sample_metadata = self._metadata_func(hit, {})
            if not isinstance(sample_metadata, dict):
                raise ValueError(
                    f"Expected the metadata_func to return a dict but got \
                        `{type(sample_metadata)}`"
                )
