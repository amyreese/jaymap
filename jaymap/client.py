# Copyright 2021 John Reese
# Licensed under the MIT License

import json
import logging
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from typing import Dict

import aiohttp

from .types import Session, Request, Response

LOG = logging.getLogger(__name__)


@dataclass(eq=False, order=False)
class JMAP:
    domain: str  # jmap.fastmail.com
    username: str  # user@fastmail.com
    password: str = field(repr=False)  # hunter42
    session: Session = field(init=False)

    stack: AsyncExitStack = field(init=False, repr=False)
    client: aiohttp.ClientSession = field(init=False, repr=False)

    @property
    def client_headers(self) -> Dict[str, str]:
        return {}

    def __init__(self, domain: str, username: str, password: str):
        self.domain = domain
        self.username = username
        self.password = password

    async def __aenter__(self) -> "JMAP":
        self.stack = AsyncExitStack()
        basic_auth = aiohttp.BasicAuth(self.username, self.password)
        self.client = await self.stack.enter_async_context(
            aiohttp.ClientSession(auth=basic_auth)
        )
        await self.init()
        return self

    async def __aexit__(self, *args) -> None:
        await self.stack.aclose()

    async def init(self) -> Session:
        discovery_url = f"https://{self.domain}/.well-known/jmap"
        async with self.client.get(discovery_url) as response:
            text = await response.text("utf-8")
            session_json = json.loads(text)
            LOG.debug(
                "JMAP Session state:\n%s",
                json.dumps(session_json, indent=4, sort_keys=True),
            )
            self.session = Session.from_json(text)

        return self.session

    def request(self, req: Request) -> Response:
        pass
