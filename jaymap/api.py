# Copyright 2022 Amethyst Reese
# Licensed under the MIT License

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Iterable, List, Union, Any, Dict

from stringcase import camelcase

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
    SetResult,
)
from jaymap.types.mail import Mailbox, Email, MailboxCondition, EmailCondition

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

    async def _request(self, method: str, **kwargs: Any) -> Invocation:
        kwargs = {
            camelcase(k.strip("_")): v for k, v in kwargs.items() if v is not None
        }
        if "accountId" not in kwargs:
            kwargs["accountId"] = self.account_id

        req = Request(
            using=[self.using], method_calls=[Invocation(method, kwargs, "c1")]
        )
        response = await self.client.request(req)
        result = response.method_responses[0]

        if result[0] != method:
            raise ValueError(result)

        return result

    async def _changes(
        self,
        *,
        since_state: str,
        max_changes: Optional[UnsignedInt] = None,
        account_id: Optional[Id] = None,
        **kwargs: Any,
    ) -> Invocation:
        method = f"{self.name}/changes"
        return await self._request(
            method,
            since_state=since_state,
            max_changes=max_changes,
            account_id=account_id,
            **kwargs,
        )

    async def _get(
        self,
        *,
        ids: Union[ResultReference, Iterable[Id], None] = None,
        properties: Optional[List[str]] = None,
        account_id: Optional[Id] = None,
        **kwargs: Any,
    ) -> Invocation:
        method = f"{self.name}/get"
        return await self._request(
            method, ids=ids, properties=properties, account_id=account_id, **kwargs
        )

    async def _query(
        self,
        *,
        filter: Union[FilterCondition, FilterOperator, None] = None,
        sort: Optional[Comparator] = None,
        position: int = 0,
        anchor: Optional[Id] = None,
        anchor_offset: int = 0,
        limit: Optional[UnsignedInt] = None,
        calculate_total: bool = False,
        account_id: Optional[Id] = None,
        **kwargs: Any,
    ) -> Invocation:
        method = f"{self.name}/query"
        return await self._request(
            method,
            filter=encode(filter),
            sort=encode(sort),
            position=position,
            anchor=anchor,
            anchor_offset=anchor_offset,
            limit=limit,
            calculate_total=calculate_total,
            account_id=account_id,
            **kwargs,
        )

    async def _set(
        self,
        *,
        if_in_state: Optional[str] = None,
        create: Optional[Dict[Id, Any]] = None,
        update: Optional[Dict[Id, List[str]]] = None,
        destroy: Optional[List[Id]] = None,
        account_id: Optional[Id] = None,
        **kwargs: Any,
    ) -> Invocation:
        method = f"{self.name}/set"
        return await self._request(
            method,
            if_in_state=if_in_state,
            create=create,
            update=update,
            destroy=destroy,
            account_id=account_id,
            **kwargs,
        )


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
        result = await self._query(
            sort_as_tree=sort_as_tree,
            filter_as_tree=filter_as_tree,
            filter=filter,
            sort=sort,
            position=position,
            anchor=anchor,
            anchor_offset=anchor_offset,
            limit=limit,
            calculate_total=calculate_total,
            account_id=account_id,
        )
        return decode(result[1], QueryResult)

    async def set(
        self,
        *,
        on_destroy_remove_emails: bool = False,
        if_in_state: Optional[str] = None,
        create: Optional[Dict[Id, Any]] = None,
        update: Optional[Dict[Id, List[str]]] = None,
        destroy: Optional[List[Id]] = None,
        account_id: Optional[Id] = None,
    ) -> SetResult[Mailbox]:
        result = await self._set(
            on_destroy_remove_emails=on_destroy_remove_emails,
            if_in_state=if_in_state,
            create=create,
            update=update,
            destroy=destroy,
            account_id=account_id,
        )
        return decode(result[1], SetResult[Mailbox])


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

    async def query(
        self,
        *,
        collapse_threads: bool = False,
        filter: Union[EmailCondition, FilterOperator, None] = None,
        sort: Optional[Comparator] = None,
        position: int = 0,
        anchor: Optional[Id] = None,
        anchor_offset: int = 0,
        limit: Optional[UnsignedInt] = None,
        calculate_total: bool = False,
        account_id: Optional[Id] = None,
    ) -> QueryResult:
        kwargs = {"collapseThreads": collapse_threads}

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

    async def set(
        self,
        *,
        if_in_state: Optional[str] = None,
        create: Optional[Dict[Id, Any]] = None,
        update: Optional[Dict[Id, List[str]]] = None,
        destroy: Optional[List[Id]] = None,
        account_id: Optional[Id] = None,
    ) -> SetResult[Email]:
        result = await self._set(
            if_in_state=if_in_state,
            create=create,
            update=update,
            destroy=destroy,
            account_id=account_id,
        )
        return decode(result[1], SetResult[Email])
