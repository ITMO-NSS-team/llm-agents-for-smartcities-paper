from typing import Any, Iterator, Sequence
from collections import defaultdict
from sortedcontainers import SortedList

from langchain_core.documents import Document

from elasticsearch.helpers import scan

from rag.loaders.utilities import es_query_all_hits
from rag.loaders.elasticsearch_loader import ElasticsearchLoader


class ElasticsearchMergedLoader(ElasticsearchLoader):
    def __init__(self,
                 grouping_key: str = 'doc_name',
                 join_separator: str = '\n\n',
                 **kwargs: Any
                 ):
        super().__init__(**kwargs)
        self._grouping_key = grouping_key
        self._join_separator = join_separator

    def lazy_load(self) -> Iterator[Document]:
        """Grouping, load, join and return documents from the Elasticsearch."""
        grouping_key2id = defaultdict(SortedList)
        for hit in scan(self.client, query=es_query_all_hits, index=self.index_name,
                        scroll=self._scroll, raise_on_error=self._raise_on_error,
                        preserve_order=self._preserve_order, size=self._size,
                        request_timeout=self._request_timeout, clear_scroll=self._clear_scroll):
            grouping_key2id[hit['_source'][self._grouping_key]].add(hit['_id'])
        validate = True
        for key, ids_list in grouping_key2id.items():
            grouped_hits = [self.client.get(index=self.index_name, id=_id) for _id in ids_list]
            yield self._parse(grouped_hits, validate)
            validate = False

    def _parse(self, merged_hits: Sequence[dict[str, Any]], validate: bool = True) -> Document:
        """Convert given list of grouped hits to merged document."""
        first_hit = merged_hits[0]

        if validate and self._content_key is not None:
            self._validate_content_key(first_hit['_source'])
        if validate and self._metadata_func is not None:
            self._validate_metadata_func(first_hit)

        texts = [self._get_text(hit['_source']) for hit in merged_hits]
        text = self._join_separator.join(texts)
        metadata = self._get_metadata(first_hit, **{self._grouping_key: first_hit['_source'][self._grouping_key]})
        return Document(page_content=text, metadata=metadata)
