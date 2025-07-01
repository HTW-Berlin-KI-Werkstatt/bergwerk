from data import ollama as data_ollama
from data import wiki as data_wiki 
from service import wiki as service_wiki
from . import config as service_config

def query_llm(textinput):

    response = data_ollama.query_llm(textinput)

    return response


def llm_training_data():

    pages = data_wiki.get_all_pages_of_category("Content")

    model_list = service_config.get_configitem("Deutsch_llm_models_training_list").value
    instruction = service_config.get_configitem("Deutsch_llm_models_training_instruction").value
    print(model_list, instruction)

    for model in model_list:

        r = data_ollama.load_model(model)

        for p in pages:

            print(f"Generating training content with {model} for page {p}")

            de_text = service_wiki.get_page(page=p, language="Deutsch").text

            prompt = instruction + "\n" + de_text 

            r = data_ollama.query_llm(prompt, model)
            full_page = data_wiki.get_entire_page(p)
            full_page += f"\n= German training data: {model}=\n" + "\n==== Prompt ====\n" + "<pre>\n" + prompt + "</pre>""\n==== Raw Model Output ====\n" + "<pre>\n" + r + "</pre>"

            data_wiki.create_or_update_page(p, full_page)


    model_list = service_config.get_configitem("English_llm_models_training_list").value
    instruction = service_config.get_configitem("English_llm_models_training_instruction").value
    print(model_list, instruction)

    for model in model_list:

        r = data_ollama.load_model(model)

        for p in pages:

            print(f"Generating training content with {model} for page {p}")

            en_text = service_wiki.get_page(page=p, language="English").text

            prompt = instruction + "\n" + en_text 

            r = data_ollama.query_llm(prompt, model)
            full_page = data_wiki.get_entire_page(p)
            full_page += f"\n= English training data: {model}=\n" + "\n==== Prompt ====\n" + "<pre>\n" + prompt + "</pre>""\n==== Raw Model Output ====\n" + "<pre>\n" + r + "</pre>"

            data_wiki.create_or_update_page(p, full_page)
                






