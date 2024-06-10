from copy import deepcopy
from typing import TextIO

import yaml
from langchain_core.documents import BaseDocumentTransformer
from transformers import AutoTokenizer

from modules.rag.pipeline.docs_processing.entities import transformer_object_dict
from modules.rag.pipeline.docs_processing.exceptions import TransformerNameError
from modules.rag.pipeline.docs_processing.models import ConfigFile


class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance


class PipelineSettings(Singleton):
    def __init__(self):
        self._config_dict: ConfigFile | None = None
        self._transformers: list[BaseDocumentTransformer] | None = None

    def make_config_structure(self, config_file: str | TextIO):
        if isinstance(config_file, str):
            with open(config_file, 'r') as f:
                yaml_config = yaml.safe_load(f)
        else:
            yaml_config = config_file
        self._config_dict = ConfigFile.model_validate(yaml_config)

        splitter_params = self._config_dict.splitter.splitter_params

        if self._config_dict.splitter.splitter_name not in transformer_object_dict:
            raise TransformerNameError('There is no DocumentTransformer related to the name: "{}"'
                                       .format(self._config_dict.splitter))
        else:
            transformer_names = ['recursive_character']
            if self._config_dict.splitter.splitter_name != 'recursive_character':
                transformer_names.append(self._config_dict.splitter.splitter_name)
            self._transformers = []
            transformer_params = []
            for transformer_name in transformer_names:
                transformer_class = transformer_object_dict[transformer_name]
                transformer_obj = transformer_class()
                transformer_params.append({key: value for key, value in splitter_params.items()
                                           if f'_{key}' in transformer_obj.__dict__ or key in transformer_obj.__dict__})

                self._transformers.append(transformer_class(**transformer_params[-1]))

        if self._config_dict.tokenizer is not None:
            tokenizer = AutoTokenizer.from_pretrained(self._config_dict.tokenizer)

            for i in range(len(self._transformers)):
                transformer = self._transformers[i]
                self._transformers[i] = transformer.from_huggingface_tokenizer(
                    tokenizer,
                    **transformer_params[i]
                )

    @property
    def config_structure(self) -> ConfigFile:
        return deepcopy(self._config_dict)

    @property
    def transformers(self) -> list[BaseDocumentTransformer]:
        return deepcopy(self._transformers)
