"""
This module interacts with the Bergwerk Wiki API to perform various operations such as logging in,
retrieving and processing data, and handling errors. It uses several external libraries including
requests, pandas, and transformers.
"""

import pandas as pd
import os
import json
from error import MissingPage, MissingSection, Unauthorized
from model.section import Section
from model.sectionwikitext import SectionWikitext
import re
from datasets import Dataset
from transformers import AutoTokenizer, DataCollatorWithPadding
from transformers import TrainingArguments, Trainer
from transformers import AutoModelForSequenceClassification
from icecream import ic
import yaml
from .connections import WikiSession

HOST = "http://wiki/w"
wiki_session = WikiSession()

def get_entire_page(page: str):
    """
    Retrieves the entire content of a specified page from the Bergwerk Wiki.

    Parameters:
    session (requests.Session): The session object used for making requests.
    page_title (str): The title of the page to retrieve.

    Returns:
    str: A string containing the page content.
    """

    session = wiki_session.get_session()

    url = HOST + "/api.php"

    page_params = {
        'action': 'parse',
        'format': 'json',
        'prop': 'wikitext',
        'page': page
    }
    response = session.get(url, params=page_params)
    response.raise_for_status()

    data = response.json()
    try:
        page_text = data['parse']['wikitext']['*']
    except KeyError:
        page_text = None

    return page_text


def get_section_wikitext(page: str, section: int) -> SectionWikitext:
    """
    Retrieves the wikitext of a specific section from a page on the Bergwerk Wiki.

    Parameters:
    page (str): The title of the page to retrieve the section from.
    section (int): The section number to retrieve the wikitext from.

    Returns:
    SectionWikitext: An object containing the wikitext of the specified section.
    """

    session = wiki_session.get_session()

    url = HOST + "/api.php"

    params = {
        "action": "parse",
        "format": "json",
        "page": page,
        "prop": "wikitext",
        "section": str(section)
    }

    response = session.get(url, params=params)
    if response.status_code == 200:
        msg = response.json()

    if 'error' in msg.keys():
        if msg['error']['code'] == "missingtitle":
            raise MissingPage(msg=f"Error: the requested page {page} does not exist.")
        if msg['error']['code'] == "nosuchsection":
            raise MissingSection(msg=f"Error: the requested section {section} does not exist.")

    parsed_response = msg['parse']

    parsed_pageid = parsed_response['pageid']
    wikitext = parsed_response['wikitext']['*']

    pattern = r'^==\s*\w+\s*=='
    filtered_wikitext = (re.sub(pattern, '', wikitext).
                         replace("<markdown>", "").
                         replace("</markdown>", "").strip())

    return SectionWikitext(page=page,
                           pageid=parsed_pageid,
                           section=section,
                           wikitext=filtered_wikitext)


def get_sections(page: str) -> list[Section]:
    """
    Retrieves all sections from a specified page on the Bergwerk Wiki.

    Parameters:
    page (str): The title of the page to retrieve sections from.

    Returns:
    list: A list of Section objects, each representing a section of the page.
    """  
    
    session = wiki_session.get_session()

    url = HOST + "/api.php"

    params = {
        "action": "parse",
        "format": "json",
        "page": page,
        "prop": "sections",
    }

    response = session.get(url, params=params)
    if response.status_code == 200:
        msg = response.json()

    if 'error' in msg.keys():
        if msg['error']['code'] == "missingtitle":
            raise MissingPage(msg=f"Error: the requested page {page} does not exist.")

    parsed_response = msg['parse']
    parsed_pageid = parsed_response['pageid']
    parsed_sections = parsed_response['sections']

    sections = []

    for section in parsed_sections:
        sections.append(Section(
            page=page,
            pageid=parsed_pageid,
            line=section['line'],
            index=section['index'],
            number=section['number'],
            toclevel=section['toclevel']
        ))

    return sections


def get_all_pages() -> list[str]:
    """
    Retrieves a list of all page titles from the Bergwerk Wiki.

    Returns:
    list[str]: A list of all page titles.
    """

    session = wiki_session.get_session()

    URL = HOST + "/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "formatversion": 2,
        "aplimit": 500,
    }

    response = session.get(URL, params=params)
    if response.status_code == 200:
        msg = response.json()

    all_pages = msg['query']['allpages']
    all_pages_titles = []

    for p in all_pages:
        all_pages_titles.append(p['title'])

    return all_pages_titles

def get_all_pages_of_category(category: str) -> list[str]:
    """
    Retrieves a list of all page titles within a specified category from the Bergwerk Wiki.

    Parameters:
    session (requests.Session): The session object used for making requests.
    category (str): The name of the category to retrieve pages from.

    Returns:
    list[str]: A list of all page titles within the specified category.
    """

    session = wiki_session.get_session()

    URL = HOST + "/api.php"

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": 10000,  # The number of pages to return (maximum of 500 for normal users)
        "format": "json"  # The format of the response (json is easier to work with in Python)

    }

    response = session.get(URL, params=params)
    if response.status_code == 200:
        msg = response.json()

    all_pages = msg['query']['categorymembers']
    all_pages_titles = []

    for p in all_pages:
        all_pages_titles.append(p['title'])

    return all_pages_titles


def get_csrf_token(session):
    """
    Retrieves a CSRF token from the Bergwerk Wiki.

    Parameters:
    session (requests.Session): The session object used for making requests.

    Returns:
    str: The CSRF token.
    """

    session = wiki_session.get_session()

    URL = HOST + "/api.php"
    response = session.get(URL, params={
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    })
    return response.json()['query']['tokens']['csrftoken']


def check_admin_token(token):
    """
    Checks if the provided token has admin privileges on the Bergwerk Wiki.

    Parameters:
    token (str): The token to check for admin privileges.

    Returns:
    bool: True if the token has admin privileges, False otherwise.
    """
    if token == get_entire_page("token"):
        return True
    else:
        return False


def export_pages(token):
    all_pages = get_all_pages()
    export = {}
    for title in all_pages:
        export[title] = get_entire_page(title)
    with open(file_path, 'w') as file:
        json.dump(dictionary, file, indent=4)

    return yaml.dump(export, default_flow_style=False)


def import_pages(pages):
    """
    Imports pages into the Bergwerk Wiki from a YAML string.

    Parameters:
    pages (str): A YAML string containing page titles and their corresponding wikitext content.

    Returns:
    None
    """
    all_pages = yaml.safe_load(pages)
    for title, wikitext in all_pages:
        ic(title)
        create_or_update_page(title, wikitext)


def create_or_update_page(title, content):
    """
    Creates or updates a page on the Bergwerk Wiki with the given wikitext content.

    Parameters:
    title (str): The title of the page to create or update.
    content (str): The wikitext content to be added to the page.

    Returns:
    None
    """
    session = wiki_session.get_session()
    csrf_token = get_csrf_token(session)
    URL = HOST + "/api.php"
    response = session.post(URL, data={
        'action': 'edit',
        'title': title,
        'text': content,
        'token': csrf_token,
        'format': 'json',
        'bot': 'True'
    })
    if 'error' in response.json():
        raise Exception(response.json()['error'])
    return response.json()


def build_intent_classifier():
    """
    Builds and trains an intent classifier using a specified dataset and model.

    Parameters:
    HOST (str): The base URL of the Bergwerk Wiki.
    token (str): The token to check for admin privileges.

    Returns:
    None
    """

    page_titles = get_all_pages()
    ic(page_titles)

    training = {}

    for t in page_titles:
        sections = get_sections(t)
        for section in sections:
            if section.line == "Training Questions":
                training[t] = get_section_wikitext(
                    t, section.index).wikitext

    counter = 0
    i = 0
    indexes = []
    sentences = []
    labels = []
    pages = []

    for k in training.keys():
        for sentence in training[k].split("\n*"):
            if "= Training Questions =" not in sentence and sentence != "":
                indexes.append(i)
                sentences.append(sentence)
                labels.append(counter)
                i += 1
        pages.append(k)

        counter += 1

    dataset = dict()
    dataset['idx'] = indexes
    dataset['label'] = labels
    dataset['sentence'] = sentences

    dataset = Dataset.from_dict(dataset)
    train_test = dataset.train_test_split(train_size=.95)

    chkpnt = "rasa/LaBSE"
    tokenizer = AutoTokenizer.from_pretrained(chkpnt)

    def tokenize_function(example):
        return tokenizer(example["sentence"], truncation=True)

    tokenized_datasets = train_test.map(tokenize_function, batched=True)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    training_args = TrainingArguments(output_dir=str("/intent_classifier/ic"),
                                      num_train_epochs=15,
                                      save_strategy="no",
                                      per_device_train_batch_size=32)

    lang_model = AutoModelForSequenceClassification.from_pretrained(
        chkpnt, num_labels=counter)

    pages_df = pd.DataFrame({"page": pages})
    os.makedirs("intent_classifier", exist_ok=True)
    pages_df.to_csv(str("/intent_classifier/ic_page_labels.csv"))

    trainer = Trainer(
        lang_model,
        training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model()


if __name__ == "__main__":
    from icecream import ic
    # export PYTHONPATH="${PYTHONPATH}:`pwd`"
    # build_intent_classifier("http://localHOST:8080")
    ic(predict("what english proficiency?"))
