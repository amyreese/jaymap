# Copyright 2021 John Reese
# Licensed under the MIT License

# pylint: disable=too-few-public-methods

"""
https://jmap.io/spec-core.html
"""

import re
from typing import Union, Dict, Tuple, Any, List, Optional

from jaymap.types.base import Datatype


class Capabilities:
    CORE = "urn:ietf:params:jmap:core"
    MAIL = "urn:ietf:params:jmap:mail"
    CONTACTS = "urn:ietf:params:jmap:contacts"
    CALENDAR = "urn:ietf:params:jmap:calendars"


class Id(str):
    _VALID = re.compile(r"[A-Za-z0-9_-]{1,255}")

    def __new__(cls, value: str):
        if not cls._VALID.fullmatch(value):
            raise ValueError(f"invalid Id {value!r}")
        return str.__new__(cls, value)  # type: ignore


class Int(int):
    _MIN = -(2 ** 53) + 1
    _MAX = 2 ** 53 - 1

    def __new__(cls, value: Union[str, int]):
        if isinstance(value, str):
            value = int(value)
        if value < cls._MIN:
            raise ValueError(f"{cls.__name__} {value!r} < {cls._MIN}")
        if value > cls._MAX:
            raise ValueError(f"{cls.__name__} {value!r} > {cls._MAX}")
        return int.__new__(cls, value)  # type: ignore


class UnsignedInt(Int):
    _MIN = 0


class Date:
    pass


class UTCDate:
    pass


class Account(Datatype):
    name: str
    is_personal: bool
    is_read_only: bool
    account_capabilities: Dict[str, Any]


class Session(Datatype):
    capabilities: Dict[str, Any]
    accounts: Dict[Id, Account]
    primary_accounts: Dict[str, Id]
    username: str
    api_url: str
    download_url: str
    upload_url: str
    event_source_url: str
    state: str


class Invocation(Tuple[str, Dict[str, Any], str]):
    def __new__(cls, name: str, arguments: Dict[str, Any], call_id: str):
        return tuple.__new__(cls, (name, arguments, call_id))


class Request(Datatype):
    using: List[str]
    method_calls: List[Invocation]
    created_ids: Optional[Dict[Id, Id]] = None


class Response(Datatype):
    method_responses: List[Invocation]
    session_state: str
    created_ids: Optional[Dict[Id, Id]] = None
