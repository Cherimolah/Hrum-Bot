import time
from hashlib import md5
import json
from urllib.parse import urlencode, quote

from aiohttp import ClientSession


class HttpClient:
    def __init__(self, proxy_url: str, user_agent: str):
        self.proxy_url = proxy_url
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Origin": "https://game.hrum.me",
            "Referer": "https://game.hrum.me/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "X-Requested-With": "org.telegram.messenger",
            "Sec-Ch-Ua": "\"Android WebView\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            'Content-Type': 'application/json',
            'User-Agent': user_agent,
        }
        self.api_key = None

    async def request(self, method: str, url: str, data: dict = None, api_key: str = None):
        if not api_key:
            api_key = self.api_key
        if not data:
            data = '{data:{}}'
        else:
            data = json.dumps(data, separators=(',', ':'))
        headers = self.headers
        api_time = str(int(time.time()))
        headers['Api-Key'] = api_key
        headers['Api-Time'] = api_time
        headers['Api-Hash'] = md5(f"{api_time}_{quote(data)}".encode('utf-8')).hexdigest()
        async with ClientSession() as session:
            async with session.request(method, url, headers=headers, data=data, proxy=self.proxy_url) as response:
                return await response.json()

    async def auth(self, web_data: str):
        data = {
            'data': {
                'initData': web_data,
                'platform': 'android',
                'chatId': '',
            }
        }
        return await self.request('POST', 'https://api.hrum.me/telegram/auth', data, 'empty')

    async def info(self):
        return await self.request('POST', 'https://api.hrum.me/user/data/all')

    async def open(self):
        return await self.request('POST', 'https://api.hrum.me/user/cookie/open', {})
