# Copyright 2021 John Reese
# Licensed under the MIT License

import asyncio
import json
import logging
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from typing import Dict, List

import aiohttp

from jaymap.types.core import Session, Request, Response

LOG = logging.getLogger(__name__)


def log_json(message: str, text: str) -> None:
    data = json.loads(text)
    LOG.debug("%s\n%s", message, json.dumps(data, indent=4, sort_keys=True))


@dataclass(eq=False, order=False)
class JMAP:
    domain: str  # jmap.fastmail.com
    username: str  # user@fastmail.com
    password: str = field(repr=False)  # hunter42
    session: Session = field(init=False)

    capabilities: List[str] = field(default_factory=list)
    account_id: str = ""

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
        await self.update_session()
        return self

    async def __aexit__(self, *args) -> None:
        await self.stack.aclose()

    async def update_session(self) -> Session:
        discovery_url = f"https://{self.domain}/.well-known/jmap"
        LOG.debug("sending auto-discovery request to %s", discovery_url)
        async with self.client.get(discovery_url) as response:
            text = await response.text("utf-8")
            if response.status != 200:
                raise ValueError(f"response error {response.status}: {text}")

            log_json("auto-discovery response", text)
            self.session = Session.from_json(text)
            self.capabilities = list(self.session.capabilities)

        return self.session

    async def request(self, req: Request) -> Response:
        api_url = self.session.api_url
        text = req.to_json()
        LOG.debug("JMAP.request(%s)\n  %s\n  %s", repr(req), api_url, text)
        async with self.client.post(api_url, data=text) as response:
            text = await response.text("utf-8")
            if response.status != 200:
                raise ValueError(f"response error {response.status}: {text}")

            log_json("API response", text)
            data = Response.from_json(text)

            if data.session_state != self.session.state:
                LOG.debug("session state changed, triggering auto-discovery")
                asyncio.create_task(self.update_session())

            return data
