# Copyright 2021 John Reese
# Licensed under the MIT License

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Iterable, List, Union

from jaymap.types.base import decode
from jaymap.types.core import (
    Id,
    GetResult,
    ResultReference,
    Invocation,
    Request,
    Capabilities,
)
from jaymap.types.mail import Mailbox, Email

if TYPE_CHECKING:
    from jaymap.client import JMAP  # pylint: disable=cyclic-import


@dataclass
class API:
    using: str = field(init=False, repr=False, default=Capabilities.CORE)
    client: "JMAP"

    @property
    def account_id(self) -> Id:
        primary_accounts = self.client.session.primary_accounts
        if self.using in primary_accounts:
            return primary_accounts[self.using]
        return primary_accounts.get(Capabilities.CORE, Id(""))


@dataclass
class MailboxAPI(API):
    using = Capabilities.MAIL

    async def get(
        self,
        *,
        ids: Union[ResultReference, Iterable[Id], None] = None,
        properties: Optional[List[str]] = None,
        account_id: Optional[Id] = None,
    ) -> GetResult[Mailbox]:
        kwargs = {"accountId": account_id or self.account_id}

        if isinstance(ids, list):
            kwargs["ids"] = ids
        elif isinstance(ids, ResultReference):
            kwargs["#ids"] = ids.to_dict()

        if properties:
            kwargs["properties"] = properties

        req = Request(
            using=list(self.client.capabilities),
            method_calls=[Invocation("Mailbox/get", kwargs, "c1")],
        )
        result = await self.client.request(req)
        name, arguments, call_id = result.method_responses[0]
        if name == "error":
            raise ValueError(name, arguments, call_id)
        if name != "Mailbox/get":
            raise ValueError(name, arguments, call_id)

        return decode(arguments, GetResult[Mailbox])


@dataclass
class EmailAPI(API):
    using = Capabilities.MAIL

    async def get(
        self,
        *,
        ids: Union[ResultReference, Iterable[Id], None] = None,
        properties: Optional[List[str]] = None,
        account_id: Optional[Id] = None,
    ) -> GetResult[Email]:
        kwargs = {"accountId": account_id or self.account_id}

        if isinstance(ids, list):
            kwargs["ids"] = ids
        elif isinstance(ids, ResultReference):
            kwargs["#ids"] = ids.to_dict()

        if properties:
            kwargs["properties"] = properties

        req = Request(
            using=list(self.client.capabilities),
            method_calls=[Invocation("Email/get", kwargs, "c1")],
        )
        result = await self.client.request(req)
        name, arguments, call_id = result.method_responses[0]
        if name == "error":
            raise ValueError(name, arguments, call_id)
        if name != "Email/get":
            raise ValueError(name, arguments, call_id)

        return GetResult[Email].from_dict(arguments)
