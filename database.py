import sqlite3

from getuseragent import UserAgent


class Database:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.connection = sqlite3.connect('database.sqlite3')
        self.cursor = self.connection.cursor()
        self.load_data()

    def load_data(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS sessions(name TEXT PRIMARY KEY, proxy_url TEXT, user_agent TEXT)')
        self.connection.commit()

    def save_proxy(self, session_name: str, proxy_url: str):
        user_agent = UserAgent('android')
        self.cursor.execute('INSERT INTO sessions VALUES(?, ?, ?)', (session_name, proxy_url, user_agent.Random()))
        self.connection.commit()

    def get_proxy(self, session_name: str):
        self.cursor.execute('SELECT proxy_url FROM sessions WHERE name = ?', (session_name,))
        response = self.cursor.fetchone()
        if not response:
            return None
        return response[0]

    def get_user_agent(self, session_name: str):
        self.cursor.execute('SELECT user_agent FROM sessions WHERE name = ?', (session_name,))
        response = self.cursor.fetchone()[0]
        return response


db = Database()
