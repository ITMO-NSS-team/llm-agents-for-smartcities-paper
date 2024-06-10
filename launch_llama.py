from transformers import BitsAndBytesConfig

from modules.definitions import ROOT
from modules.model import UrbAssistant


if __name__ == '__main__':
    sys_prompt = '''Your name is Larry. You are smart AI assistant, You have high experitce in field of city building, 
    urbanistic and Structure of St. Petersburg. 
    Answer the question following rules below. For answer you must use provided by user context.
    Rules:
    1. You must use only provided information for the answer.
    2. Add a unit of measurement to an answer.
    3. If there are several organizations in the building, all of them should be mentioned in the answer.
    4. The building's address (street, house number, building) in the user's question should exactly 
    match a building address from the context.
    5. For answer you should take only that infromation from context, which exactly match a building 
    address (street, house number, building) from the user's question.
    6. If provided by user context for a given address has "null" or "None" for the property, 
    it means the data about this property of the building is absent.
    7. In questions about building failure, 0 in the context's corresponding field means "no", and 1 - means "yes".
    8. If data for an answer is absent, answer that data was not provided or absent and mention for 
    what field there was no data.
    9. If you do not know how to answer the questions, say so.
    10. Before give an answer to the user question, provide explanation. Mark the answer with keyword "ANSWER", 
    and explanation with "EXPLANATION". Both answer and explanation must be in Russian language
    11. Answer should be three sentences maximum.'''
    context = '''В настоящее время уровень конкурентоспособности становится базовым условием успешности
    и устойчивости функционирования социально-экономических систем субъектов Российской Федерации, 
    которые постепенно становятся самостоятельными экономическими субъектами национальной экономики, 
    участниками глобальных международных экономических процессов. 
    Выявление и развитие конкурентных преимуществ способствует активизации внутренних возможностей Санкт-Петербурга 
    для достижения целей социально-экономического развития, более эффективному и рациональному использованию имеющегося ресурсного потенциала его территории. Конкурентные преимущества Санкт-Петербурга определены исходя из анализа сильных и слабых сторон социально-экономического развития Санкт-Петербурга, возможностей и факторов, влияющих на уровень его конкурентоспособности, которые в совокупности создают для Санкт-Петербурга определенное превосходство по сравнению с другими российскими и зарубежными городами, а также другими субъектами Российской Федерации, располагающими сходными характеристиками. Определение сильных и слабых сторон социально-экономического развития Санкт-Петербурга базируется на выводах и сравнениях, сделанных в результате оценки достигнутых целей социально-экономического развития, и представлено в разрезе отраслей, сфер и направлений социально-экономического развития Санкт-Петербурга.'''
    question = 'Как оценивается конкурентоспособность Санкт-Петербурга на глобальном уровне?'
    
    bnb_config = BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True)
    
    assistant = UrbAssistant('meta-llama/Meta-Llama-3-8B-Instruct', quantization_config=bnb_config)
    assistant.set_sys_prompt(sys_prompt)
    assistant.init_retirever(pth=str(ROOT / 'data'/ 'docs' / 'example.docx'), collection_name='test_1')
    user_message = f'Question:{question}\nContext:{context}'
    ans = assistant(user_message, temperature=0.015, top_p=.05)
    print(ans.split('ANSWER: ')[-1])
    print('Done.')