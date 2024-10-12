import re
from typing import Optional

proxy_regexp = re.compile(r'^(?:(?P<protocol>.+)://)?(?P<login>[^:]+):(?P<password>[^@|:]+)[@|:](?P<host>[^:]+):(?P<port>\d+)$')


class ProxyError(Exception):
    pass


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
        raise ProxyError('Invalid proxy')
