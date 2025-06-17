import redis
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends
from models.models import *
import jwt
from models.models import User
import requests 

r = redis.Redis(host='redis', port=6379, decode_responses=True, db=0)


SECRET_KEY = r.hget("config:sec", "secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MEDIAWIKI_API_URL = "http://wiki/w/api.php"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class MediaWikiAuth:
    def __init__(self, api_url):
        self.api_url = api_url
        self.session = requests.Session()

    def get_login_token(self):
        """Step 1: Get login token"""
        params = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        response = self.session.get(self.api_url, params=params)
        response.raise_for_status()
        return response.json()["query"]["tokens"]["logintoken"]

    def login(self, username, password):
        """Step 2: Login with username/password"""
        token = self.get_login_token()
        data = {
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": token,
            "format": "json"
        }
        response = self.session.post(self.api_url, data=data)
        response.raise_for_status()
        result = response.json()

        if result.get("login", {}).get("result") == "Success":
            return True
        else:
            print("Login failed:", result)
            return False

    def is_user_admin(self, username):
        """Step 3: Check if user is in 'sysop' group"""
        params = {
            "action": "query",
            "list": "users",
            "ususers": username,
            "usprop": "groups",
            "format": "json"
        }
        response = self.session.get(self.api_url, params=params)
        response.raise_for_status()
        user_data = response.json()["query"]["users"][0]
        return "sysop" in user_data.get("groups", [])


def authenticate_admin(username, password):
    auth = MediaWikiAuth(MEDIAWIKI_API_URL)
    if not auth.login(username, password):
        return False
    if not auth.is_user_admin(username):
        return False
    return True



def authenticate_user(username: str, password: str):
    if not authenticate_admin(username, password):
        return False 
    user =  User(username=username)
    return user 


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


