import asyncio
import random
from urllib.parse import unquote
from datetime import datetime, timedelta

from loguru import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView

from database import db
from http_client import HttpClient
from config import ENTRY_TIMEOUT, AUTO_CLAIM_DAILY_REWARD, AUTO_CLAIM_RIDDLE, API_ID, API_HASH
from utils import parse_proxy


class Bot:
    def __init__(self, session_name: str):
        self.session_name = session_name
        self._query_data = db.get_query_data(session_name)
        self._proxy_url: str = db.get_proxy(session_name)
        self._user_agent: str = db.get_user_agent(session_name)
        self.http_client = HttpClient(self._proxy_url, self._user_agent)

    async def load_query_data(self):
        if self._query_data:
            return self._query_data
        client = Client(self.session_name, API_ID, API_HASH,
                        workdir='sessions/', proxy=parse_proxy(db.get_proxy(self.session_name)))
        await client.connect()
        logger.info(f'{self.session_name} | Session validated')
        peer = await client.resolve_peer('hrummebot')
        response = await client.invoke(
            RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=True,
                url='https://game.hrum.me/'
            )
        )
        tg_web_data = unquote(response.url).split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion',
                                                                                        maxsplit=1)[0]
        logger.info(f'{self.session_name} | Web View params got')
        await client.disconnect()
        return tg_web_data

    async def run(self):
        while True:
            try:
                if not self._query_data:
                    web_params = await self.load_query_data()
                else:
                    web_params = self._query_data
                api_key = web_params.split('&hash=', maxsplit=1)[1]
                self.http_client.api_key = api_key
                auth = await self.http_client.auth(web_params)
                if auth['success']:
                    logger.success(f'{self.session_name} | Auth successful')
                else:
                    logger.error(f'{self.session_name} | Auth failed')
                    return
                info = await self.http_client.info()
                daily_rewards = (await self.http_client.daily_info())['data']
                if AUTO_CLAIM_DAILY_REWARD:
                    for day, state in daily_rewards.items():
                        if state == 'canTake':
                            logger.info(f'{self.session_name} | Available daily reward for day number {day}')
                            response = await self.http_client.claim_daily(day)
                            if response['success']:
                                logger.success(f'{self.session_name} | Successfully claimed daily reward. '
                                               f'Balance {response["data"]["hero"]["token"]}')
                if AUTO_CLAIM_RIDDLE:
                    quest_id = None
                    key = None
                    for quest in info['data']['dbData']['dbQuests']:
                        if quest['key'].startswith('riddle_'):
                            quest_id = quest['key']
                            key = quest.get('checkData')
                            break
                    if not key:
                        logger.error(f'{self.session_name} | Riddle key not found')
                        quest_id = None
                    if quest_id:
                        more_info = await self.http_client.more_info()
                        completed = False
                        for quest in more_info['data']['quests']:
                            if quest['key'] == quest_id and quest['isRewarded']:
                                completed = True
                                break
                        if not completed:
                            logger.info(f'{self.session_name} | Available riddle')
                            response = await self.http_client.check_riddle(quest_id, key)
                            if response['data']['result']:
                                logger.info(f'{self.session_name} | Success check riddle')
                                response = await self.http_client.claim_riddle(quest_id, key)
                                if response['success']:
                                    logger.success(f'{self.session_name} | Successfully claimed riddle')
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
                    logger.success(f'{self.session_name} | Cookie opened: {cookies[0]["text"]}')
                seconds = int((next_time - now).total_seconds())
                logger.info(f'{self.session_name} | Cookie will be available in {seconds} seconds')
                time_to_sleep = random.randint(*ENTRY_TIMEOUT)
                logger.info(f'{self.session_name} | Sleeping for {time_to_sleep} seconds')
                await asyncio.sleep(time_to_sleep)
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f'{self.session_name} | Error: {e}')
                await asyncio.sleep(10)
            # finally:
            #     if self.tg_client.is_connected:
            #         await self.tg_client.disconnect()
