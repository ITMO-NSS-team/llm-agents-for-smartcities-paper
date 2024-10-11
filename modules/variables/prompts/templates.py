llama_70b_template = (
    r'{"job_id":"${job_id}",'
    r'"meta":{"temperature":"${temperature}",'
    r'"tokens_limit":"${token_limit}",'
    r'"stop_words":["string"]},'
    r'"content":"<|begin_of_text|><|start_header_id|>system<|end_header_id|>${system_prompt}'
    r"<|eot_id|><|start_header_id|>user<|end_header_id|>${user_prompt}"
    r'<|eot_id|><|start_header_id|>assistant<|end_header_id|>"}'
)
llama_8b_template = (
    r'{"model":"llama3_8b",'
    r'"messages":[{"role":"system",'
    r'"content":"${system_prompt}"},'
    r'{"role":"user","content":"${user_prompt}"}]}'
)
all_gpt_template = r'[{"role":"system","content":"${system_prompt}"},{"role":"user","content":"${user_prompt}"}]'

llama_70b_int4_template = (
    r'{"job_id":"${job_id}",'
    r'"meta":{"temperature":"${temperature}",'
    r'"tokens_limit":"${token_limit}",'
    r'"stop_words":[]},'
    r'"messages":[{"role":"system",'
    r'"content":"${system_prompt}"},'
    r'{"role":"user","content":"${user_prompt}"}]}'
)
