# Copyright 2021 John Reese
# Licensed under the MIT License

"""
Base datatype implementation with encoding/decoding support
"""

import json
import re
import sys
from dataclasses import dataclass, field, is_dataclass, asdict, fields
from textwrap import indent
from typing import (
    get_type_hints,
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

from stringcase import camelcase
from typing_inspect import (
    is_generic_type,
    is_optional_type,
    is_union_type,
    is_typevar,
    get_origin,
    get_args,
    get_generic_bases,
)

T = TypeVar("T")

INDENT = "    "
PRIMITIVES = (bool, float, int, bytes, str, type(None), Any)


def is_primitive(ftype: Type) -> bool:
    try:
        return ftype in PRIMITIVES or issubclass(ftype, PRIMITIVES)
    except TypeError:
        return False


def decode(obj: Any, hint: Type, hint_args: Any = ()) -> Any:
    ftype = hint
    origin = get_origin(ftype)
    bases = get_generic_bases(ftype)
    targs = get_args(ftype)

    if hint_args and any(is_typevar(t) for t in targs):
        targs = hint_args

    if ftype in PRIMITIVES:
        return obj

    if is_optional_type(ftype):
        if obj is None:
            return None

        real_args = [t for t in targs if t is not type(None)]
        if len(real_args) > 1:
            raise NotImplementedError(f"can't decode union types ({real_args})")
        ftype = real_args[0]
        origin = get_origin(ftype)
    elif is_union_type(ftype):
        raise NotImplementedError(f"can't decode union types ({targs})")

    if is_primitive(ftype):
        return ftype(obj)

    if is_datatype(ftype) or (origin and is_dataclass(origin)):
        if not isinstance(obj, dict):
            raise TypeError(f"invalid data {obj!r} for {ftype}")

        kwargs: Dict[str, Any] = {}

        namespace = sys.modules[ftype.__module__].__dict__
        if origin and is_dataclass(origin):
            type_hints = get_type_hints(origin, namespace)
        else:
            type_hints = get_type_hints(ftype, namespace)
        for fname, ft in type_hints.items():
            key = camelcase(fname.strip("_"))

            if key in obj:
                kwargs[fname] = decode(obj[key], ft, targs)

        return ftype(**kwargs)

    if is_generic_type(ftype):
        while origin is None and bases:
            if len(bases) > 1:  # pragma: nocover
                raise NotImplementedError(f"can't decode multiple bases {ftype}")
            ftype = bases[0]
            origin = get_origin(ftype)
            bases = get_generic_bases(ftype)
            targs = get_args(ftype)

        if origin in (dict, Dict, Mapping):
            if not is_primitive(targs[0]):
                raise NotImplementedError(f"can't decode object keys {ftype}")
            ftype = targs[1]

            if ftype in PRIMITIVES:
                return dict(obj)
            else:
                return {k: decode(v, ftype) for k, v in obj.items()}

        if origin in (tuple, Tuple):
            return tuple(decode(v, ftype) for v, ftype in zip(obj, targs))

        if origin in (set, Set):
            ftype = targs[0]

            if ftype in PRIMITIVES:
                return set(obj)
            else:
                return set(decode(v, ftype) for v in obj)

        if origin in (list, List):
            ftype = targs[0]

            if ftype in PRIMITIVES:
                return list(obj)
            else:
                return [decode(v, ftype) for v in obj]

    raise NotImplementedError(f"failed to decode {obj} as type {hint}")


def encode(obj: Any, hint: Type) -> Any:
    ftype = hint
    if obj is None or is_primitive(ftype):
        return obj

    if is_optional_type(ftype):
        targs = [t for t in get_args(ftype) if t is not type(None)]
        if len(targs) > 1:
            raise NotImplementedError(f"can't encode union types ({targs})")
        ftype = targs[0]
    elif is_union_type(ftype):
        raise NotImplementedError(f"can't encode union types ({get_args(ftype)})")

    if is_generic_type(ftype):
        origin = get_origin(ftype)
        bases = get_generic_bases(ftype)
        targs = get_args(ftype)

        while origin is None and bases:
            if len(bases) > 1:  # pragma: nocover
                raise NotImplementedError(f"can't encode multiple bases {ftype}")
            ftype = bases[0]
            origin = get_origin(ftype)
            bases = get_generic_bases(ftype)
            targs = get_args(ftype)

        if origin in (dict, Dict, Mapping):
            if not is_primitive(targs[0]):
                raise NotImplementedError(f"can't encode object keys {ftype}")
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

        namespace = sys.modules[ftype.__module__].__dict__
        for fname, ftype in get_type_hints(obj, namespace).items():
            key = camelcase(fname.strip("_"))
            value = getattr(obj, fname)

            result[key] = encode(value, ftype)

        return result

    raise NotImplementedError(f"failed to encode {hint}({type(obj)!r})")


class Datatype:
    """Dataclass derivative with json encode/decode capabilities"""

    def __init_subclass__(cls):
        dataclass(repr=False)(cls)

    def __repr__(self) -> str:
        parts: List[str] = []
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, list) and value:
                inner = "\n".join(f"{v!r}," for v in value)
                part = f"[\n{indent(inner, INDENT)}\n]"
            elif isinstance(value, dict) and value:
                inner = "\n".join(f"{k!r}: {v!r}," for k, v in value.items())
                part = f"{{\n{indent(inner, INDENT)}\n}}"
            else:
                part = repr(value)
            parts.append(f"{field.name}={part},")
        inner = indent("\n".join(parts), INDENT)
        return f"{self.__class__.__name__}(\n{inner}\n)"

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cast(cls, decode(data, cls))

    @classmethod
    def from_list(cls: Type[T], data: List[Dict[str, Any]]) -> List[T]:
        return [cls.from_dict(v) for v in data]

    @classmethod
    def from_json(cls: Type[T], text: str) -> T:
        return cls.from_dict(json.loads(text))

    def to_dict(self) -> Dict[str, Any]:
        return encode(self, self.__class__)

    def to_json(self, **kwargs: Any) -> str:
        kwargs.setdefault("sort_keys", True)
        return json.dumps(self.to_dict(), **kwargs)


def is_datatype(obj: Any) -> bool:
    return is_dataclass(obj) and (
        isinstance(obj, Datatype) or (type(obj) == type and issubclass(obj, Datatype))
    )
