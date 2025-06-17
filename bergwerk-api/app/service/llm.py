from data import ollama as data_ollama
from data import wiki as data_wiki 
from service import wiki as service_wiki
from . import config as service_config

def query_llm(textinput):

    response = data_ollama.query_llm(textinput)

    return response


def llm_training_data():

    pages = data_wiki.get_all_pages_of_category("Content")

    model_list = [m.strip() for m in service_wiki.get_configitem("Deutsch_llm_models_training_list").value.split(",")]
    instruction = service_config.get_configitem("Deutsch_llm_models_training_instruction").value

    for model in model_list:

        data_ollama.load_model(model)
        print(f"Try to load model {model}")

        for p in pages:


            try:

                print(f"Generating training content with {model} for page {p}")

                en_text = service_wiki.get_page(page=p, language="Deutsch").text

                prompt = instruction + "\n" + en_text 

                r = data_ollama.query_llm(prompt, model)
                full_page = data_wiki.get_entire_page(p)
                full_page += f"\n= Deutsche Trainingsdaten vom {model}=\n" + "\n==== Prompt ====\n" + "<pre>\n" + prompt + "</pre>""\n==== Raw Model Output ====\n" + "<pre>\n" + r + "</pre>"

                data_wiki.create_or_update_page(p, full_page)
                
            except Exception as e:
                print(e)
                continue

    model_list = [m.strip() for m in service_wiki.get_configitem("English_llm_models_training_list").value.split(",")]
    instruction = service_config.get_configitem("English_llm_models_training_instruction").value

    for model in model_list:

        data_ollama.load_model(model)
        print(f"Try to load model {model}")

        for p in pages:


            try:

                print(f"Generating training content with {model} for page {p}")

                en_text = service_wiki.get_page(page=p, language="English").text

                prompt = instruction + "\n" + en_text 

                r = data_ollama.query_llm(prompt, model)
                full_page = data_wiki.get_entire_page(p)
                full_page += f"\n= English Training Questions from {model}=\n" + "\n==== Prompt ====\n" + "<pre>\n" + prompt + "</pre>""\n==== Raw Model Output ====\n" + "<pre>\n" + r + "</pre>"

                data_wiki.create_or_update_page(p, full_page)
                
            except Exception as e:
                print(e)
                continue





