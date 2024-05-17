from typing import Any


class LLAMAHandler:
    """
    Class for interaction with llama models.
    """
    def __init__(self, model, tokenizer, *args, **kwargs) -> None:
        self.model = model # Initialized model
        self.tokenizer = tokenizer
        self._prompt = None # Set up default prompt
        
    def set_prompt(self):
        """Method for prompt configuration."""
        pass
    
    def generate(self, generation_config: Any, *args, **kwargs):
        """Generate an answer given prompt and generation config."""
        pass