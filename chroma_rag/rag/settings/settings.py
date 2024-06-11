from os.path import dirname
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChromaSettings(BaseSettings):
    # Chroma DB settings
    chroma_host: str = '10.32.1.34'
    chroma_port: int = 9941
    allow_reset: bool = False

    # Documents collection's settings
    collection_name: str = 'my_collection2'
    embedding_name: str = 'intfloat/multilingual-e5-large'
    embedding_host: str = 'http://10.32.1.34:9942/embed'
    distance_fn: str = 'cosine'

    # Documents' processing settings
    docs_processing_config: str = str(Path(dirname(dirname(__file__)) + '/configs/' + 'docs_processing_config.yaml'))
    docs_collection_path: str = str(Path(Path(__file__).parent.parent.parent, 'docs', 'strategy.pdf'))
    # docs_collection_path: str = str(Path(dirname(dirname(dirname(__file__))) + '/docs/' + 'example.docx'))

    # model_config = SettingsConfigDict(
    #     env_file=Path(dirname(dirname(__file__)) + '/configs/' + 'chroma.env'),
    #     env_file_encoding='utf-8',
    #     extra='ignore',
    # )


settings = ChromaSettings()
