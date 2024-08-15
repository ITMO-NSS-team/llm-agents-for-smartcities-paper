import os
import pathlib


ROOT = pathlib.Path(__file__).parent.parent.resolve()
SMALL_LLAMA = os.environ.get('LLAMA_URL_8b')
LARGE_LLAMA = os.environ.get('LLAMA_URL')
