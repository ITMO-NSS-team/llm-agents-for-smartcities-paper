import logging

from chroma_rag.rag.pipeline.etl_pipeline import DocsExtractPipeline
from chroma_rag.rag.settings.pipeline_settings import PipelineSettings
from chroma_rag.rag.settings.settings import ChromaSettings
from chroma_rag.rag.settings.settings import settings as default_settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_documents_to_chroma_db(
    settings: ChromaSettings | None = None,
    processing_batch_size: int = 100,
    loading_batch_size: int = 32,
    **kwargs,
) -> None:
    """Loads documents into a Chroma DB collection using a processing pipeline.

    Args:
        settings (Optional[ChromaSettings]): The settings for configuring the Chroma DB and document processing pipeline.
            If not provided, default settings are used.
        processing_batch_size (int): The size of the batches for document processing. Defaults to 100.
        loading_batch_size (int): The size of the batches for loading documents into the Chroma DB. Defaults to 32.
        **kwargs: Additional keyword arguments to update document transformers in the pipeline.

    Returns:
        None
    """
    if settings is None:
        settings = default_settings

    logger.info(
        f"Initializing batch generator with processing_batch_size: {processing_batch_size},"
        f" loading_batch_size: {loading_batch_size}"
    )

    pipeline_settings = PipelineSettings()
    pipeline_settings.make_config_structure(settings.docs_processing_config)

    # Documents loading and processing
    DocsExtractPipeline(pipeline_settings).go_to_next_step(
        docs_collection_path=settings.docs_collection_path
    ).update_docs_transformers(**kwargs).go_to_next_step(
        batch_size=processing_batch_size
    ).store_settings(settings).load(loading_batch_size=loading_batch_size)
