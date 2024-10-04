import asyncio
import random
from urllib.parse import unquote
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from loguru import logger

from database import db
from http_client import HttpClient
from config import ENTRY_TIMEOUT, AUTO_CLAIM_DAILY_REWARD


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
        while True:
            try:
                await self.tg_client.connect()
                logger.info(f'{self.tg_client.name} | Session validated')
                web_params = await self.get_init_params()
                logger.info(f'{self.tg_client.name} | Web View params got')
                await self.tg_client.disconnect()
                api_key = unquote(web_params.split('&hash=', maxsplit=1)[1])
                self.http_client.api_key = api_key
                auth = await self.http_client.auth(web_params)
                if auth['success']:
                    logger.success(f'{self.tg_client.name} | Auth successful')
                else:
                    logger.error(f'{self.tg_client.name} | Auth failed')
                    return
                info = await self.http_client.info()
                daily_rewards = (await self.http_client.daily_info())['data']
                if AUTO_CLAIM_DAILY_REWARD:
                    for day, state in daily_rewards.items():
                        if state == 'canTake':
                            logger.info(f'{self.tg_client.name} | Available daily reward for day number {day}')
                            response = await self.http_client.claim_daily(day)
                            if response['success']:
                                logger.success(f'{self.tg_client.name} | Successfully claimed daily reward. '
                                               f'Balance {response["data"]["hero"]["token"]}')
                has_cookie = info['data']['hero']['cookies']
                now = datetime.utcnow()
                if now.hour >= 7:
                    next_time = now + timedelta(days=1)
                    next_time = datetime(next_time.year, next_time.month, next_time.day, 7, 0, 0)
                else:
                    next_time = datetime(now.year, now.month, now.day, 7, 0, 0)
                if has_cookie:
                    cookies = (await self.http_client.open())['data']['history']
                    cookies.sort(key=lambda x: datetime.strptime(x['updateDate'], '%Y-%m-%d %H:%M:%S'), reverse=True)
                    await self.http_client.open()
                    logger.success(f'{self.tg_client.name} | Cookie opened: {cookies[0]["text"]}')
                seconds = int((next_time - now).total_seconds())
                logger.info(f'{self.tg_client.name} | Cookie will be available in {seconds} seconds')
                time_to_sleep = random.randint(*ENTRY_TIMEOUT)
                logger.info(f'{self.tg_client.name} | Sleeping for {time_to_sleep} seconds')
                await asyncio.sleep(time_to_sleep)
            except Exception as e:
                logger.error(f'{self.tg_client.name} | Error: {e}')
                await asyncio.sleep(10)
            finally:
                if self.tg_client.is_connected:
                    await self.tg_client.disconnect()
