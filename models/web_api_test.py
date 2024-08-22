import json

from new_web_api import NewWebAssistant

from models.prompts.strategy_prompt import accessibility_sys_prompt


if __name__ == "__main__":
    sys_prompt = accessibility_sys_prompt
    path_to_file_with_context = (
        "/home/kolyan288/Data/Отраслевой_контекст_–_Культура_и_досуг.json"
    )
    files = [
        path_to_file_with_context
    ]  # если нужно собрать контекст с нескольких файлов, добавить пути
    context = ""

    for file in files:
        with open(file) as f:
            context += str(json.load(f))

    model = NewWebAssistant()
    model.set_sys_prompt(sys_prompt)
    model.add_context(context)

    response = model(
        "Какова обеспеченность объектами культуры и досуга?", as_json=True
    )
    print(response)

    # sys_prompt = accessibility_sys_prompt
    #
    # context = """В настоящее время уровень конкурентоспособности становится базовым условием успешности и устойчивости
    #     функционирования социально-экономических систем субъектов Российской Федерации, которые постепенно становятся
    #     самостоятельными экономическими субъектами национальной экономики, участниками глобальных международных экономических
    #     процессов. Выявление и развитие конкурентных преимуществ способствует активизации внутренних возможностей Санкт-Петербурга
    #     для достижения целей социально-экономического развития, более эффективному и рациональному использованию имеющегося ресурсного
    #     потенциала его территории. Конкурентные преимущества Санкт-Петербурга определены исходя из анализа сильных и слабых сторон
    #     социально-экономического развития Санкт-Петербурга, возможностей и факторов, влияющих на уровень его конкурентоспособности,
    #     которые в совокупности создают для Санкт-Петербурга определенное превосходство по сравнению с другими российскими и
    #     зарубежными городами, а также другими субъектами Российской Федерации, располагающими сходными характеристиками.
    #     Определение сильных и слабых сторон социально-экономического развития Санкт-Петербурга базируется на выводах и сравнениях,
    #     сделанных в результате оценки достигнутых целей социально-экономического развития, и представлено в разрезе отраслей,
    #     сфер и направлений социально-экономического развития Санкт-Петербурга."""
    #
    # model = WebAssistant()
    # model.set_sys_prompt(sys_prompt)
    # model.add_context(context)
    #
    # response = model("Как оценивается конкурентоспособность Санкт-Петербурга на глобальном уровне?", as_json=True)
    # pprint(response)
