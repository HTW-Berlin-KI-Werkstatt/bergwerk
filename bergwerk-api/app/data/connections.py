"""
This module contains classes for handling initial connections to the wiki and the database.
"""


import requests
import os
import sys
from time import sleep
import mariadb

class WikiSession:
    def __init__(self):
        self.session = None
        self.connected = False

        while not self.connected:
            try:
                self.session = self.login()
                self.connected = True
                print("Wiki session established.")

            except requests.exceptions.RequestException as e:
                print(f"Wiki connection failed: {e}, retrying in 5 secs...")
                sleep(5)


    def login(self):

        url = "http://bergwerk-wiki/w/api.php"
        session = requests.Session()

        # Get login token
        response = session.get(url, params={
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        })
        login_token = response.json()['query']['tokens']['logintoken']

        # Log in
        response = session.post(url, data={
            'action': 'login',
            'lgname': os.getenv('BOT_USERNAME'),
            'lgpassword': os.getenv('BOT_PASSWORD'),
            'lgtoken': login_token,
            'format': 'json'
        })

        if response.json()['login']['result'] != 'Success':
            raise Exception('Failed to log in')
        
        return session
    
    def get_session(self):
        return self.session


class DatabaseSession:
    """
    Manages database connections and cursors.
    """
    def __init__(self):
        self.connected = False
        self.cursor = None
        self.conn = None        
    
        while not self.connected:
            try:
                self.cursor, self.conn = self.login()
                self.connected = True
                print("DB connection established.")
            except requests.exceptions.RequestException as e:
                print(f"DB connection failed: {e}, retrying in 5 secs...")
                sleep(5)
                

    def login(self):

        try:
            conn = mariadb.connect(
                user=os.getenv('SQL_USERNAME'),
                password=os.getenv('SQL_PASSWORD'),
                host="bergwerk-db",
                port=3306,
                database="tracker_db"
            )

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)


        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS tracker (
            record_id INT AUTO_INCREMENT PRIMARY KEY,  
            id VARCHAR(255),                          
            ts BIGINT,                     
            role VARCHAR(50),                          
            text TEXT,                                 
            buttons TEXT
        );
        """

        try:
            cursor.execute(create_table_query)
            print("Table 'tracker' created successfully (or already exists).")
        except mariadb.Error as e:
            print(f"Error creating table: {e}")

        conn.commit()

        return cursor, conn
    
    def get_cursor_conn(self):

        if self.conn.open:
            return self.cursor, self.conn
        else:
            self.cursor, self.conn = self.login()
            print("Reconnected to mysql.")
            return self.cursor, self.conn