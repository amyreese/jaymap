# Copyright 2022 Amethyst Reese
# Licensed under the MIT License

import asyncio
import json
import logging
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from typing import Dict, List, Coroutine, Optional

import aiohttp

from jaymap.api import MailboxAPI, EmailAPI
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
    subscription: Optional[asyncio.Task] = field(init=False, repr=False, default=None)

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

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self.subscription is not None:
            if exc_type:  # exception
                self.subscription.cancel()
            await self.subscription
        await self.stack.aclose()

    async def close(self) -> None:
        if self.subscription is not None:
            self.subscription.cancel()

    @property
    def mailbox(self) -> MailboxAPI:
        return MailboxAPI(self)

    @property
    def email(self) -> EmailAPI:
        return EmailAPI(self)

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

    async def subscribe(
        self, callback: Coroutine[None, None, None], types: Optional[List[str]] = None
    ) -> None:
        """
        Create a connection to the server and call the given coroutine with any updates.
        """

        if self.subscription is not None:
            raise ValueError("already subscribed!")

        async def inner():
            try:
                async with self.client.get(
                    self.session.event_source_url,
                    params={
                        "types": ",".join(types) if types else "*",
                        "closeafter": "state",
                        "ping": 30,
                    },
                ) as response:
                    while True:
                        line = await response.content.readline()
                        if not line:
                            LOG.info("subscription closed")
                            break

                        await callback(line)
                        await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                LOG.debug("subscription cancelled")
            except Exception:  # pylint: disable=broad-except
                LOG.exception("subscription failed")
            finally:
                self.subscription = False

        self.subscription = asyncio.create_task(inner())
        LOG.debug("subscribed: %s", self.subscription)
