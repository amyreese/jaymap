# Copyright 2021 John Reese
# Licensed under the MIT License

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Iterable, List, Union, Any, Dict

from jaymap.types.base import decode, encode
from jaymap.types.core import (
    Id,
    GetResult,
    ResultReference,
    Invocation,
    Request,
    Capabilities,
    Comparator,
    QueryResult,
    FilterCondition,
    FilterOperator,
    UnsignedInt,
)
from jaymap.types.mail import Mailbox, Email, MailboxCondition

if TYPE_CHECKING:
    from jaymap.client import JMAP  # pylint: disable=cyclic-import


@dataclass
class API:
    using: str = field(init=False, repr=False, default=Capabilities.CORE)
    client: "JMAP"

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("API", "")

    @property
    def account_id(self) -> Id:
        primary_accounts = self.client.session.primary_accounts
        if self.using in primary_accounts:
            return primary_accounts[self.using]
        return primary_accounts.get(Capabilities.CORE, Id(""))

    async def _get(
        self,
        *,
        ids: Optional[Iterable[Id]] = None,
        properties: Optional[List[str]] = None,
        account_id: Optional[Id] = None,
        **kwargs: Any,
    ) -> Invocation:
        method = f"{self.name}/get"
        kwargs["accountId"] = account_id or self.account_id

        if ids:
            kwargs["ids"] = ids
        if properties:
            kwargs["properties"] = properties

        req = Request(
            using=[self.using], method_calls=[Invocation(method, kwargs, "c1")]
        )
        response = await self.client.request(req)
        result = response.method_responses[0]

        if result[0] != method:
            raise ValueError(result)

        return result

    async def _query(
        self,
        *,
        kwargs: Optional[Dict[str, Any]] = None,
        filter: Union[FilterCondition, FilterOperator, None] = None,
        sort: Optional[Comparator] = None,
        position: int = 0,
        anchor: Optional[Id] = None,
        anchor_offset: int = 0,
        limit: Optional[UnsignedInt] = None,
        calculate_total: bool = False,
        account_id: Optional[Id] = None,
    ) -> Invocation:
        method = f"{self.name}/query"

        if not kwargs:
            kwargs = {}
        kwargs["accountId"] = account_id or self.account_id

        for key, value in (
            ("filter", encode(filter)),
            ("sort", encode(sort)),
            ("position", position),
            ("anchor", anchor),
            ("anchorOffset", anchor_offset),
            ("limit", limit),
            ("calculateTotal", calculate_total),
        ):
            if value:
                kwargs[key] = value

        req = Request(
            using=[self.using], method_calls=[Invocation(method, kwargs, "c1")]
        )
        response = await self.client.request(req)
        result = response.method_responses[0]

        if result[0] != method:
            raise ValueError(result)

        return result


@dataclass
class MailboxAPI(API):
    using = Capabilities.MAIL
    method = "Mailbox"

    async def get(
        self,
        *,
        ids: Union[ResultReference, Iterable[Id], None] = None,
        properties: Optional[List[str]] = None,
        account_id: Optional[Id] = None,
    ) -> GetResult[Mailbox]:
        result = await self._get(ids=ids, properties=properties, account_id=account_id)
        return decode(result[1], GetResult[Mailbox])

    async def query(
        self,
        *,
        sort_as_tree: bool = False,
        filter_as_tree: bool = False,
        filter: Union[MailboxCondition, FilterOperator, None] = None,
        sort: Optional[Comparator] = None,
        position: int = 0,
        anchor: Optional[Id] = None,
        anchor_offset: int = 0,
        limit: Optional[UnsignedInt] = None,
        calculate_total: bool = False,
        account_id: Optional[Id] = None,
    ) -> QueryResult:
        kwargs = {"sortAsTree": sort_as_tree, "filterAsTree": filter_as_tree}

        result = await self._query(
            kwargs=kwargs,
            filter=filter,
            sort=sort,
            position=position,
            anchor=anchor,
            anchor_offset=anchor_offset,
            limit=limit,
            calculate_total=calculate_total,
            account_id=account_id,
        )
        return QueryResult.from_dict(result[1])


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
        result = await self._get(ids=ids, properties=properties, account_id=account_id)
        return decode(result[1], GetResult[Email])
