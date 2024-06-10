from typing import Optional
import logging

from modules.rag.pipeline.etl_pipeline import DocsExtractPipeline
from modules.rag.settings.pipeline_settings import PipelineSettings
from modules.rag.settings.settings import ChromaSettings, settings as default_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_documents_to_chroma_db(settings: Optional[ChromaSettings] = None,
                                processing_batch_size: int = 100,
                                loading_batch_size: int = 32,
                                **kwargs) -> None:

    if settings is None:
        settings = default_settings

    logger.info(
        f'Initializing batch generator with processing_batch_size: {processing_batch_size},'
        f' loading_batch_size: {loading_batch_size}'
    )

    pipeline_settings = PipelineSettings()
    pipeline_settings.make_config_structure(settings.docs_processing_config)

    # Documents loading and processing
    DocsExtractPipeline(pipeline_settings) \
        .go_to_next_step(docs_collection_path=settings.docs_collection_path) \
        .update_docs_transformers(**kwargs) \
        .go_to_next_step(batch_size=processing_batch_size) \
        .store_settings(settings) \
        .load(loading_batch_size=loading_batch_size)
