from sqlalchemy import create_engine
import pandas as pd
import requests
import os


def sql2pd(database, table):
    user = os.getenv('SQL_USER')
    password = os.getenv('SQL_PASS')
    connection_string = f"mysql+mysqlconnector://{user}:{password}@bergwerk-db/{database}"
    engine = create_engine(connection_string)
    df = pd.read_sql_table(table, con=engine)
    return df

def login():
    url = "http://bergwerk-wiki/w/api.php"
    session = requests.Session()

    response = session.get(url, params={
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    })
    login_token = response.json()['query']['tokens']['logintoken']

    user = os.getenv('BOT_USERNAME')
    password = os.getenv('BOT_PASSWORD')

    response = session.post(url, data={
        'action': 'login',
        'lgname': user,
        'lgpassword': password,
        'lgtoken': login_token,
        'format': 'json'
    })

    if response.json()['login']['result'] != 'Success':
        raise Exception('Failed to log in')

    return session


def get_entire_page(page: str):
    url = "http://bergwerk-wiki/w/api.php"

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

def get_csrf_token(session):

    url = "http://bergwerk-wiki/w/api.php"
    response = session.get(url, params={
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    })
    return response.json()['query']['tokens']['csrftoken']

def create_or_update_page(title, content):
    csrf_token = get_csrf_token(session)
    url = "http://bergwerk-wiki/w/api.php"
    response = session.post(url, data={
        'action': 'edit',
        'title': title,
        'text': content,
        'token': csrf_token,
        'format': 'json'
    })
    if 'error' in response.json():
        raise Exception(response.json()['error'])
    return response.json()

def gen_overview_page(df):
        
    page_content = """[[Category:Tracker]]\n= Conversation Tracker ="""

    overview = f"\n\nThere are {len(df.id.unique())} conversations stored in the conversation tracker.\n"
    page_content += overview

    dft = df.groupby(by="id").ts.min().reset_index()
    dft['datetime'] = pd.to_datetime(dft['ts'], unit = "s")
    dft['year'] = dft.datetime.dt.year
    dft['month'] = dft.datetime.dt.month
    dft['month_name'] = dft.datetime.dt.month_name()
    dft['day'] = dft.datetime.dt.day
    dft['ymd'] = dft['datetime'].dt.strftime('%Y%m%d')
    dft['ymdhm'] = dft['datetime'].dt.strftime('%Y%m%d%H%M')
    dft['human_date'] = dft['datetime'].dt.strftime('%d. %B %Y')
    dft = dft.sort_values("ts", ascending=False)

    all_conversations = ""
    months_with_data = dft.human_date.unique().astype(list)

    for m in months_with_data:
        all_conversations += f"= {m} =\n"
        dfm = dft[(dft["human_date"] == m)]
        ids_of_day = dfm.id.unique().astype(list)
        for id in ids_of_day:
                ymd = dfm[dfm.id == id].ymd.values[0]
                all_conversations += f"* [[{ymd}:{id}|{id}]]\n"

    page_content += all_conversations

    return dft, page_content


session = login()
