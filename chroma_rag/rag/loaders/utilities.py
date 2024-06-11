from typing import Any
import json

from rag.settings.es_settings import settings


es_query_all_hits = settings.es_query_all_hits


def get_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return json.dumps(content) if content else ""
    else:
        return str(content) if content is not None else ""


def json_metadata_func(record: dict, metadata: dict) -> dict:
    new_metadata = dict()
    new_metadata['id'] = metadata.get('seq_num')
    if 'metadata' in record:
        record = record['metadata']

    for field in settings.metadata_fields:
        new_metadata[field] = record.get(field, 'empty')

    return new_metadata


def elasticsearch_metadata_func(hit: dict, metadata: dict) -> dict:
    new_metadata = dict()
    new_metadata['id'] = metadata.get('id')
    hit_metadata = hit['_source']
    if 'metadata' in hit_metadata:
        hit_metadata = hit_metadata['metadata']

    for field in settings.metadata_fields:
        new_metadata[field] = hit_metadata.get(field, 'empty')

    return new_metadata


def elasticsearch_merged_metadata_func(hit: dict, metadata: dict) -> dict:
    new_metadata = dict()
    hit_metadata = hit['_source']
    if 'metadata' in hit_metadata:
        hit_metadata = hit_metadata['metadata']

    for field in settings.metadata_fields:
        new_metadata[field] = hit_metadata.get(field, 'empty')

    new_metadata.update(metadata)
    return new_metadata
