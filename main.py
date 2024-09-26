import asyncio
import os
import sys
from typing import Optional
import re
import glob

from bot import Bot
from pyrogram import Client
from loguru import logger
from aiohttp import ClientSession, ClientTimeout

from config import API_ID, API_HASH
from database import db


proxy_regexp = re.compile(r'^(?:(?P<protocol>.+)://)?(?P<login>[^:]+):(?P<password>[^@|:]+)[@|:](?P<host>[^:]+):(?P<port>\d+)$')


async def run_process():
    names = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob('sessions/*.session')]
    clients = [Client(name, api_id=API_ID, api_hash=API_HASH,
                      workdir='sessions/', proxy=parse_proxy(db.get_proxy(name))) for name in names]
    tasks = [Bot(client).run() for client in clients]
    await asyncio.gather(*tasks)


def parse_proxy(proxy: str) -> Optional[dict[str, str]]:
    if not proxy:
        return
    if matcher := proxy_regexp.match(proxy):
        return {
            'scheme': matcher.group('protocol'),
            'hostname': matcher.group('host'),
            'port': int(matcher.group('port')),
            'username': matcher.group('login'),
            'password': matcher.group('password'),
        }
    else:
        print('Invalid proxy')
        exit(1)


async def check_proxy(proxy_url: str):
    async with ClientSession(timeout=ClientTimeout(5)) as session:
        async with session.get('https://ipinfo.io/json', proxy=proxy_url) as response:
            response.raise_for_status()
            data = await response.json()
    logger.success(f'Proxy validated! IP: {data["ip"]} city: {data["city"]}')


async def create_session():
    if not os.path.isdir("sessions"):
        os.mkdir("sessions")
    session_name = input("Enter session name: ")
    proxy = input("Enter proxy (for example: http://user:password@123.123.123.123:8080). Press enter to continue: ")
    if proxy:
        await check_proxy(proxy)
    client = Client(session_name, proxy=parse_proxy(proxy), api_id=API_ID, api_hash=API_HASH, workdir='sessions/')
    async with client:
        user_data = await client.get_me()
    db.save_proxy(session_name, proxy)
    logger.success(f"Created session {session_name}: @{user_data.username} {user_data.first_name} {user_data.last_name}")


async def main():
    args = sys.argv[1:]
    if len(args) == 0:
        choice = input('Welcome to Hrumbot by Cherimolah!\nSelect an action:\n\n'
                       '1: Create session\n2: Start bot\n\nYour choice: ')
        try:
            choice = int(choice)
        except ValueError:
            print('Invalid choice!')
            return
        match choice:
            case 1:
                await create_session()
                return
            case 2:
                await run_process()
            case _:
                print('Invalid choice!')
                return
    elif len(args) == 2 and args[0] in ('-a', '--action') and args[1] in ('1', '2'):
        if args[1] == '1':
            await create_session()
        elif args[1] == '2':
            await run_process()


if __name__ == '__main__':
    asyncio.run(main())
