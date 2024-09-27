import asyncio
import random
from urllib.parse import unquote
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from loguru import logger

from database import db
from http_client import HttpClient


class Bot:
    def __init__(self, telegram_client: Client):
        self.tg_client = telegram_client
        self._proxy_url: str = db.get_proxy(telegram_client.name)
        self._user_agent: str = db.get_user_agent(telegram_client.name)
        self.http_client = HttpClient(self._proxy_url, self._user_agent)

    async def get_init_params(self):
        peer = await self.tg_client.resolve_peer('hrummebot')
        response = await self.tg_client.invoke(
            RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=True,
                url='https://game.hrum.me/'
            )
        )
        tg_web_data = unquote(response.url).split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]
        return tg_web_data

    async def run(self):
        await self.tg_client.connect()
        while True:
            try:
                logger.info(f'{self.tg_client.name} | Session validated')
                web_params = await self.get_init_params()
                logger.info(f'{self.tg_client.name} | Web View params got')
                api_key = unquote(web_params.split('&hash=', maxsplit=1)[1])
                self.http_client.api_key = api_key
                auth = await self.http_client.auth(web_params)
                if auth['success']:
                    logger.success(f'{self.tg_client.name} | Auth successful')
                else:
                    logger.error(f'{self.tg_client.name} | Auth failed')
                    return
                info = await self.http_client.info()
                update_date = info['data']['hero']['updateDate']
                update_date = datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
                now = datetime.utcnow()
                tomorrow = now + timedelta(days=1)
                tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0, 0)
                if (now - update_date).total_seconds() > 86400:
                    cookies = (await self.http_client.open())['data']['history']
                    cookies.sort(key=lambda x: datetime.strptime(x['updateDate'], '%Y-%m-%d %H:%M:%S'), reverse=True)
                    logger.success(f'{self.tg_client.name} | Cookie opened: {cookies[0]["text"]}')
                    logger.info(f'{self.tg_client.name} | Cookie will be available in {(tomorrow - now).total_seconds()} seconds')
                    await asyncio.sleep((tomorrow - now).total_seconds() + random.randint(30, 120))
                else:
                    logger.info(f'{self.tg_client.name} | Cookie will be available in {(tomorrow - now).total_seconds()} seconds')
                    await asyncio.sleep((tomorrow - now).total_seconds() + random.randint(30, 120))
            except:
                await asyncio.sleep(10)
