# Copyright 2021 John Reese
# Licensed under the MIT License

# pylint: disable=too-few-public-methods

"""
https://jmap.io/spec-core.html
"""

import re
import time
from datetime import datetime, timezone
from typing import Union, Dict, Tuple, Any, List, Optional, Type

from jaymap.types.base import Datatype, T


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

    def __repr__(self) -> str:
        return f"Id({super().__repr__()})"


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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class UnsignedInt(Int):
    _MIN = 0


class Date(str):
    """"2014-10-30T06:12:00+05:00"""

    DT_PARSE = r"%Y-%m-%dT%H:%M:%S%z"
    DT_FMT = r"%Y-%m-%dT%H:%M:%S%z"
    UTC_FMT = r"%Y-%m-%dT%H:%M:%SZ"

    def __new__(cls, value: str, dt: Optional[datetime] = None):
        return super().__new__(cls, value)

    def __init__(self, value: str, dt: Optional[datetime] = None):
        if dt is None:
            self.datetime = datetime.strptime(value, self.DT_PARSE)
        else:
            self.datetime = dt

    @classmethod
    def from_datetime(cls: Type[T], source: datetime) -> "T":
        if source.tzinfo in (None, timezone.utc):
            value = source.strftime(cls.UTC_FMT)
        else:
            value = source.strftime(cls.DT_FMT)
            value = f"{value[:-2]}:{value[-2:]}"
        return cls(value, source)


class UTCDate(Date):
    """"2014-10-30T06:12:00Z"""

    DTF = r"%Y-%m-%dT%H:%M:%SZ"
    DTP = r"%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, value: str, dt: Optional[datetime] = None):
        if dt and dt.tzinfo not in (None, timezone.utc):
            raise ValueError(f"invalid timezone {dt.tzinfo} for UTCDate")
        super().__init__(value, dt)
        if self.datetime.tzinfo not in (None, timezone.utc):
            raise ValueError(
                f"invalid parsed timezone {self.datetime.tzinfo} for UTCDate"
            )

    @classmethod
    def from_datetime(cls: Type[T], source: datetime) -> "T":
        if source.tzinfo not in (None, timezone.utc):
            raise ValueError(f"invalid timezone {source.tzinfo} for UTCDate")
        return super().from_datetime(source)


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
