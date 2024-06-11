from typing import Any

from pydantic import BaseModel


class ConfigLoader(BaseModel):
    doc_path: str = ''
    save_path: str = ''
    loader_name: str
    parsing_params: dict[str, Any] = dict()


class ConfigSplitter(BaseModel):
    splitter_name: str | None = None
    splitter_params: dict[str, Any] = dict()


class ConfigFile(BaseModel):
    loader: ConfigLoader
    splitter: ConfigSplitter = ConfigSplitter()
    tokenizer: str | None = None
