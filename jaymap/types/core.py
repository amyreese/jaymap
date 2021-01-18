# Copyright 2021 John Reese
# Licensed under the MIT License

# pylint: disable=too-few-public-methods

"""
https://jmap.io/spec-core.html
"""

import re
from dataclasses import dataclass, field, is_dataclass, asdict, fields
from typing import (
    Union,
    Dict,
    Any,
    Mapping,
    List,
    Tuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from dataclasses_json import LetterCase, DataClassJsonMixin
from dataclasses_json.api import _process_class
from stringcase import camelcase, snakecase
from typing_inspect import is_generic_type, is_optional_type, get_origin, get_args

T = TypeVar("T")

PRIMITIVES = (bool, float, int, str, type(None), Any)


def normalized_dict(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    return {camelcase(key.strip("_")): value for key, value in pairs}


def default_encode(obj: Any, hint: Optional[Type] = None) -> Any:
    if is_dataclass(obj):
        return asdict(obj, dict_factory=normalized_dict)
    try:
        return obj.encode()
    except AttributeError:
        return obj


def is_primitive(ftype: Type) -> bool:
    try:
        return ftype in PRIMITIVES or issubclass(ftype, PRIMITIVES)
    except TypeError:
        return False


def decode(obj: Any, ftype: Type) -> Any:
    if ftype in PRIMITIVES:
        return obj

    if is_primitive(ftype):
        return ftype(obj)

    print(ftype, is_datatype(ftype))
    if is_datatype(ftype):
        if not isinstance(obj, dict):
            raise TypeError(obj)

        kwargs: Dict[str, Any] = {}

        for field in fields(ftype):
            ft = field.type
            fname = field.name
            key = camelcase(fname.strip("_"))

            kwargs[fname] = decode(obj[key], ft)

        print(f"{ftype}(**{kwargs})")
        return ftype(**kwargs)

    if is_optional_type(ftype):
        if obj is None:
            return None

        targs = [t for t in get_args(ftype) if t is not type(None)]
        if len(targs) > 1:
            raise NotImplementedError(f"can't decode union types ({targs})")
        ftype = targs[0]

    if is_generic_type(ftype):
        origin = get_origin(ftype)
        targs = get_args(ftype)

        if origin in (dict, Dict, Mapping):
            if not is_primitive(targs[0]):
                raise NotImplementedError(f"can't encode {ftype}")
            ftype = targs[1]

            if is_primitive(ftype):
                return obj
            else:
                return {
                    k: decode(v, ftype) for k, v in obj.items()
                }

        if origin in (tuple, Tuple):
            return tuple(decode(v, ftype) for v, ftype in zip(obj, targs))

        if origin in (set, Set):
            ftype = targs[0]

            if is_primitive(ftype):
                return set(obj)
            else:
                return set(decode(v, ftype) for v in obj)

        if origin in (list, List):
            ftype = targs[0]

            if is_primitive(ftype):
                return list(obj)
            else:
                return [decode(v, ftype) for v in obj]

    print(f"fallback decode: {ftype}({obj})")
    return ftype(obj)

def encode(obj: Any, ftype: Type) -> Any:
    if obj is None or is_primitive(ftype):
        return obj

    if is_optional_type(ftype):
        targs = [t for t in get_args(ftype) if t is not type(None)]
        if len(targs) > 1:
            raise NotImplementedError(f"can't encode union types ({targs})")
        ftype = targs[0]

    if is_generic_type(ftype):
        origin = get_origin(ftype)
        targs = get_args(ftype)

        if origin in (dict, Dict, Mapping):
            if not is_primitive(targs[0]):
                raise NotImplementedError(f"can't encode {ftype}")
            ftype = targs[1]

            if is_primitive(ftype):
                return obj
            else:
                return {
                    camelcase(k.strip("_")): encode(v, ftype) for k, v in obj.items()
                }

        if origin in (tuple, Tuple):
            return [encode(v, ftype) for v, ftype in zip(obj, targs)]

        if origin in (set, list, Sequence, Set):
            ftype = targs[0]

            if is_primitive(ftype):
                return list(obj)
            else:
                return [encode(v, ftype) for v in obj]

    if is_primitive(ftype):
        return obj

    if isinstance(obj, Datatype):
        result: Dict[str, Any] = {}

        for field in fields(obj):
            ftype = field.type
            fname = field.name
            key = camelcase(fname.strip("_"))
            value = getattr(obj, fname)

            result[key] = encode(value, ftype)

        return result

    raise NotImplementedError(f"can't encode {ftype}({type(obj)!r})")


class Datatype:
    """Dataclass derivative with json encode/decode capabilities"""

    def __init_subclass__(cls):
        dataclass(cls)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cast(cls, decode(data, cls))

    def to_dict(self) -> Dict[str, Any]:
        return encode(self, self.__class__)


def is_datatype(obj: Any) -> bool:
    return is_dataclass(obj) and (
        isinstance(obj, Datatype) or (type(obj) == type and issubclass(obj, Datatype))
    )


def datatype(cls: Type) -> Type:
    """stdlib dataclasses with dataclass_json mixin, but typecheck friendly"""
    cls = dataclass(cls)
    cls = _process_class(cls, LetterCase.CAMEL, None)
    return cls


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


# @datatype
class Account(Datatype):
    name: str
    is_personal: bool
    is_read_only: bool
    account_capabilities: Dict[str, Any]


# @datatype
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


Invocation = Tuple[str, Dict[str, Any], str]


# @datatype
class Request(Datatype):
    using: List[str]
    method_calls: List[Invocation]
    created_ids: Optional[Dict[Id, Id]] = None


# @datatype
class Response(Datatype):
    method_responses: List[Invocation]
    session_state: str
    created_ids: Optional[Dict[Id, Id]] = None


# @datatype
class Object(Datatype):
    def get(
        self,
        account_id: Id,
        ids: Optional[List[Id]] = None,
        properties: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Invocation]:
        return []

    def changes(
        self,
        account_id: Id,
        since_state: str,
        max_changes: Optional[UnsignedInt] = None,
    ) -> List[Invocation]:
        pass

    def set(self):
        pass
