from langchain_core.prompts import PromptTemplate

# Prompts for the function calling LLM which is meant to use tools
fc_sys_prompt = """You are a helpful assistant with access to the following functions. "
Use them if required - {tools}."""

fc_sys_prompt_template = PromptTemplate(
    input_variables=["tools"],
    template=fc_sys_prompt
)

fc_user_prompt = """Extract all relevant data for answering this question: {question}\n"
You MUST return ONLY the function names separated by spaces.\n
Do NOT return any other additional text."""

fc_user_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=fc_user_prompt
)

binary_fc_user_prompt = """Extract all relevant data for answering this question: {question}\n
You MUST return ONLY the function name. 
Do NOT return any other additional text."""

binary_fc_user_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=binary_fc_user_prompt
)

# Prompts for regular LLM used to check FC LLM's answer
base_sys_prompt = "You are a good assistant, who will be offered with 100$ tips for each correct answer."

# Prompt to check if the FC LLM chose the right functions for the accessibility pipeline
ac_cor_user_prompt = """[Instruction]: You are given a question, functions descriptions and an answer. 
Your task is to compare the chosen function with the question and the descriptions and determine 
if the function was selected correctly. If the chosen function is correct, return the function name. 
If the function is selected incorrectly, return the name of the correct function.\n
[Question]: {question}.\n
[Answer]: {answer}.\n
[Function Descriptions]: {tools}.\n
You MUST return ONLY the correct functions in this format:\n
[Correct answer]: correct function.
Do NOT return Context."""

ac_cor_user_prompt_template = PromptTemplate(
    input_variables=["question", "answer", "tools"],
    template=ac_cor_user_prompt
)

# Prompt to check if the FC LLM chose the right pipeline
pip_cor_user_prompt = """[Instruction]: You are given a question, descriptions of 2 functions and an answer from another 
Llama model, which has chosen one of these functions. Your task is to compare 
the chosen function with the question and the descriptions and determine 
if the function was selected correctly. If the chosen function is correct, 
return the function name. If the function is selected incorrectly, return the name 
of another function.\n
[Question]: {question}.\n
[Answer]: {answer}.\n
[Function Descriptions]: {tools}.\n
[Task]: 
Compare the chosen function with the function descriptions and the question to determine if the function 
was selected correctly. Return the name of correct function in this format: 
[Correct answer]: correct function.
Do NOT return Context."""

pip_cor_user_prompt_template = PromptTemplate(
    input_variables=["question", "answer", "tools"],
    template=pip_cor_user_prompt
)
