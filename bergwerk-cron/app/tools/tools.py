from sqlalchemy import create_engine
import pandas as pd
import requests
import os
import redis 


def sql2pd(database, table):
    user = os.getenv('SQL_USERNAME')
    password = os.getenv('SQL_PASSWORD')
    connection_string = f"mysql+mysqlconnector://{user}:{password}@db/{database}"
    engine = create_engine(connection_string)
    df = pd.read_sql_table(table, con=engine)
    return df

def login():
    url = "http://wiki/w/api.php"
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
    url = "http://wiki/w/api.php"

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

    url = "http://wiki/w/api.php"
    response = session.get(url, params={
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    })
    return response.json()['query']['tokens']['csrftoken']

def upload_image(image_path):
    """Uploads an image to the wiki and returns the filename if successful."""
    csrf_token = get_csrf_token(session)
    url = "http://wiki/w/api.php"

    with open(image_path, 'rb') as file:
        response = session.post(url, files={'file': file}, data={
            'action': 'upload',
            'filename': os.path.basename(image_path),
            'token': csrf_token,
            'format': 'json',
            'ignorewarnings': 1  # Prevent stopping on duplicate file warnings
        })

    response_data = response.json()
    if 'error' in response_data:
        raise Exception(f"Image upload failed: {response_data['error']}")

    return response_data.get('upload', {}).get('filename', os.path.basename(image_path))

def create_or_update_page(title, content, images=None):
    """Creates or updates a wiki page, optionally uploading and embedding images."""
    csrf_token = get_csrf_token(session)
    url = "http://wiki/w/api.php"

    uploaded_images = []
    if images:
        for image_path in images:
            try:
                uploaded_filename = upload_image(image_path)
                uploaded_images.append(uploaded_filename)
            except Exception as e:
                print(f"Failed to upload {image_path}: {e}")

    # Append uploaded images to page content
    if uploaded_images:
        image_texts = [f"[[File:{img}|thumb]]" for img in uploaded_images]
        content += "\n\n" + "\n".join(image_texts)

    response = session.post(url, data={
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

class Config:

    def __init__(self):
        self.config = {}
        self.r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True, encoding="utf-8")


    def get_value(self, k):
        value = self.r.hget("config:app", k)
        if value is None:
            raise KeyError(f"Key '{k}' not found in config:app")
        return value.replace("\\n\\n", "\n\n")