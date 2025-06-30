from model.pageconfidence import PageConfidence
from model.section import Section
from model.menu import MenuItem, MenuResponse
from model.configuration import ConfigItem
from data import wiki as data_wiki
from data import redis as data_redis
from error import MissingLanguage, MissingClassifier
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import pandas as pd
from datetime import datetime
import re


def get_language_specific_sections(page: str, language: str) -> list[Section]:
    sections = data_wiki.get_sections(page=page)

    language_sections: list[Section] = []

    for s in sections:
        if s.line == language:
            number = float(s.number)

    if not 'number' in locals():
        raise MissingLanguage(msg=f"Language {language} is not available for page {page}.")

    for s in sections:
        if float(s.number) > number and float(s.number) < (number + 1):
            language_sections.append(s)

    return language_sections


def get_page(page: str, language: str) -> MenuResponse:
    sections = get_language_specific_sections(page=page, language=language)

    for s in sections:
        if s.line == "Buttons":
            menuitems = data_wiki.get_section_wikitext(
                page=page, section=int(s.index)).wikitext
        if s.line == "Markdown":
            text = data_wiki.get_section_wikitext(
                page=page, section=int(s.index)).wikitext

    menuitemlist: list[MenuItem] = []

    if 'menuitems' in locals():
        menuitems = menuitems.replace(
            "== Buttons ==", "").strip("\n").split("\n")
        for menuitem in menuitems:
            if menuitem == "":
                continue
            _menuitem = menuitem.replace("* [[", "").replace("]]", "")
            link = _menuitem.split("|")[0]
            title = _menuitem.split("|")[1]
            menuitemlist.append(MenuItem(title=title, link=link))

    return MenuResponse(title=page,
                        text=text,
                        menuitems=menuitemlist
                        )


def predict(textinput: str) -> list[PageConfidence]:
    try:
        tokenizer = AutoTokenizer.from_pretrained("/intent_classifier/ic")
        model = AutoModelForSequenceClassification.from_pretrained(
            "/intent_classifier/ic")
    except: 
        print("No intent classifier found.")
        raise MissingClassifier(msg="The intent classifier is not available.")

    encoding = tokenizer(textinput, return_tensors="pt")
    outputs = model(**encoding)[0].detach().numpy()

    pages_df = pd.read_csv(
        "/intent_classifier/ic_page_labels.csv", index_col=0)
    pages_df['confidence'] = outputs[0]

    pages_df = pages_df.sort_values(by=['confidence'], axis=0, ascending=False)

    pc = []
    for idx in pages_df.index:
        pc.append(PageConfidence(
            title=pages_df.loc[idx, 'page'], confidence=pages_df.loc[idx, 'confidence']))
    return pc


def track_text(uid, role, text):
    tracker_page = datetime.now().strftime("%Y%m%d") + "_" + uid
    wikitext_history = data_wiki.get_entire_page(page=tracker_page)
    if wikitext_history is None:
        wikitext = "[[Category:Tracker]]\n'''" + role + ":'''" + text + "<br>"
    else:
        wikitext = wikitext_history + "<strong>" + role + \
            "</strong> <small>(" + datetime.now().strftime("%H:%M") + \
            ")</Small>:<markdown>" + text + "</markdown><br>"

    data_wiki.create_or_update_page(title=tracker_page, content=wikitext)




if __name__ == "__main__":
    get_page(page="start", language="English")
