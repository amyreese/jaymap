# Copyright 2021 John Reese
# Licensed under the MIT License

import re
from dataclasses import dataclass
from typing import NewType, Union, Dict, Any, List, Tuple, Optional, Type

from dataclasses_json import dataclass_json, LetterCase


def datatype(cls: Type) -> Type:
    cls = dataclass(cls)
    return dataclass_json(letter_case=LetterCase.CAMEL)(cls)


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


@datatype
class Account:
    name: str
    is_personal: bool
    is_read_only: bool
    account_capabilities: Dict[str, Any]


@datatype
class Session:
    capabilities: Dict[str, Any]
    accounts: Dict[Id, Account]
    primary_accounts: Dict[str, Id]
    username: str
    api_url: str
    download_url: str
    upload_url: str
    event_source_url: str
    state: str


Invocation = NewType("Invocation", Tuple[str, Dict[str, Any], str])


@datatype
class Request:
    using: List[str]
    method_calls: List[Invocation]
    created_ids: Optional[Dict[Id, Id]] = None


@datatype
class Response:
    method_responses: List[Invocation]
    session_state: str
    created_ids: Optional[Dict[Id, Id]] = None
