# Copyright 2021 John Reese
# Licensed under the MIT License

import re
from dataclasses import dataclass
from typing import NewType, Union, Dict, Any, List, Tuple, Optional


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


@dataclass
class Account:
    name: str
    isPersonal: bool
    isReadOnly: bool
    accountCapabilities: Dict[str, Any]


@dataclass
class Session:
    capabilities: Dict[str, Any]
    accounts: Dict[Id, Account]
    primaryAccounts: Dict[str, Id]
    username: str
    apiUrl: str
    downloadUrl: str
    uploadUrl: str
    eventSourceUrl: str
    state: str


Invocation = NewType("Invocation", Tuple[str, Dict[str, Any], str])


@dataclass
class Request:
    using: List[str]
    methodCalls: List[Invocation]
    createdIds: Optional[Dict[Id, Id]] = None


@dataclass
class Response:
    methodResponses: List[Invocation]
    sessionState: str
    createdIds: Optional[Dict[Id, Id]] = None
