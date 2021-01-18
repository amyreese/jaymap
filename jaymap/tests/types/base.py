# Copyright 2021 John Reese
# Licensed under the MIT license

from typing import Tuple, Dict, Any, Optional, List, Union, Set, Iterable
from unittest import TestCase

from jaymap.types import base


class MyInt(int):
    pass


class CustomTuple(Tuple[str, str]):
    pass


class Foo(base.Datatype):
    name: str
    from_: int
    items: List[MyInt]
    bucket_values: Dict[str, MyInt]
    maybe: Optional[CustomTuple]


class Nested(base.Datatype):
    foos: List[Foo]
    maybe: Optional[Foo]


class BaseTypes(TestCase):
    def test_is_primitive(self):
        for t in (str, int, bool, float, type(None), Any):
            with self.subTest(f"is_primitive({t!r})"):
                self.assertTrue(base.is_primitive(t))

        for t in ([1, 2], (1, 2), {1: 2}, Foo("a", 1, [], {}, None)):
            with self.subTest(f"is_primitive({t!r})"):
                self.assertFalse(base.is_primitive(type(t)))

    def test_decode_primitives(self):
        sentinel = object()

        for value, vtype, expected in (
            (True, bool, True),
            (False, bool, False),
            (123, int, 123),
            (123, MyInt, MyInt(123)),
            (b"name", bytes, b"name"),
            ("name", str, "name"),
            (None, type(None), None),
            (sentinel, Any, sentinel),
            (True, Optional[bool], True),
            (None, Optional[bool], None),
            (123, Optional[MyInt], MyInt(123)),
            (None, Optional[MyInt], None),
        ):
            with self.subTest((value, vtype, expected)):
                result = base.decode(value, vtype)
                self.assertEqual(result, expected)
                self.assertEqual(type(result), type(expected))

    def test_decode_datatype(self):
        result = base.decode(
            {
                "name": "something",
                "from": 1234,
                "items": [1, 3, 9],
                "bucketValues": {"foo": 1, "bar": 2},
                "maybe": None,
            },
            Foo,
        )
        expected = Foo(
            name="something",
            from_=1234,
            items=[1, 3, 9],
            bucket_values={"foo": 1, "bar": 2},
            maybe=None,
        )
        self.assertEqual(result, expected)
        self.assertIsInstance(result.items[0], MyInt)
        self.assertIsInstance(result.bucket_values["foo"], MyInt)

        result = base.decode(
            {
                "foos": [
                    {
                        "name": "something",
                        "from": 1234,
                        "items": [1, 3, 9],
                        "bucketValues": {"foo": 1, "bar": 2},
                        "maybe": None,
                    },
                    {
                        "name": "else",
                        "from": 1234,
                        "items": [1, 3, 9],
                        "bucketValues": {"foo": 1, "bar": 2},
                        "maybe": None,
                    },
                ],
                "maybe": {
                    "name": "another",
                    "from": 1234,
                    "items": [1, 3, 9],
                    "bucketValues": {"foo": 1, "bar": 2},
                    "maybe": None,
                },
            },
            Nested,
        )
        expected = Nested(
            foos=[
                Foo(
                    name="something",
                    from_=1234,
                    items=[1, 3, 9],
                    bucket_values={"foo": 1, "bar": 2},
                    maybe=None,
                ),
                Foo(
                    name="else",
                    from_=1234,
                    items=[1, 3, 9],
                    bucket_values={"foo": 1, "bar": 2},
                    maybe=None,
                ),
            ],
            maybe=Foo(
                name="another",
                from_=1234,
                items=[1, 3, 9],
                bucket_values={"foo": 1, "bar": 2},
                maybe=None,
            ),
        )
        self.assertEqual(result, expected)

    def test_decode_collections(self):
        for value, vtype, expected in (
            ([1, 2, 3, 4], List[int], [1, 2, 3, 4]),
            ([1, 2, 3, 4], Set[int], {1, 2, 3, 4}),
        ):
            with self.subTest((value, vtype, expected)):
                result = base.decode(value, vtype)
                self.assertEqual(result, expected)

        for value, vtype, expected in (
            ([1, 2, 3, 4], List[MyInt], [1, 2, 3, 4]),
            ([1, 2, 3, 4], Set[MyInt], {1, 2, 3, 4}),
        ):
            with self.subTest((value, vtype, expected)):
                result = base.decode(value, vtype)
                self.assertEqual(result, expected)
                for v in result:
                    self.assertIsInstance(v, MyInt)

    def test_decode_unsupported_types(self):
        with self.assertRaisesRegex(NotImplementedError, "can't decode union types"):
            base.decode(123, Union[int, str])

        with self.assertRaisesRegex(NotImplementedError, "can't decode union types"):
            base.decode(123, Union[int, str, None])

        with self.assertRaisesRegex(NotImplementedError, "can't decode union types"):
            base.decode(123, Optional[Union[int, str]])

        with self.assertRaisesRegex(NotImplementedError, "can't decode object keys"):
            base.decode(123, Dict[Foo, str])

        with self.assertRaisesRegex(NotImplementedError, "failed to decode"):
            base.decode(123, Iterable[int])

        class Frob:
            pass

        with self.assertRaisesRegex(NotImplementedError, "failed to decode"):
            base.decode(123, Frob)

    def test_decode_bad_input(self):
        with self.assertRaisesRegex(TypeError, r"invalid data .* for .*Foo"):
            base.decode([1, 2], Foo)

    def test_encode_primitives(self):
        sentinel = object()

        for value, vtype, expected in (
            (True, bool, True),
            (False, bool, False),
            (123, int, 123),
            (123, MyInt, 123),
            (MyInt(123), MyInt, MyInt(123)),
            (b"name", bytes, b"name"),
            ("name", str, "name"),
            (None, type(None), None),
            (sentinel, Any, sentinel),
            (True, Optional[bool], True),
            (None, Optional[bool], None),
            (MyInt(123), Optional[MyInt], MyInt(123)),
            (None, Optional[MyInt], None),
        ):
            with self.subTest((value, vtype, expected)):
                result = base.encode(value, vtype)
                self.assertEqual(result, expected)
                self.assertEqual(type(result), type(expected))

    def test_encode_datatype(self):
        result = base.encode(
            Foo(
                name="something",
                from_=1234,
                items=[1, 3, 9],
                bucket_values={"foo": 1, "bar": 2},
                maybe=None,
            ),
            Foo,
        )
        expected = {
            "name": "something",
            "from": 1234,
            "items": [1, 3, 9],
            "bucketValues": {"foo": 1, "bar": 2},
            "maybe": None,
        }
        self.assertEqual(result, expected)

    def test_encode_collections(self):
        for value, vtype, expected in (
            ([1, 2, 3, 4], List[int], [1, 2, 3, 4]),
            ({1, 2, 3, 4}, Set[int], [1, 2, 3, 4]),
            ([1, 2, 3, 4], List[MyInt], [1, 2, 3, 4]),
            ({1, 2, 3, 4}, Set[MyInt], [1, 2, 3, 4]),
        ):
            with self.subTest((value, vtype, expected)):
                result = base.encode(value, vtype)
                self.assertEqual(result, expected)

    def test_encode_unsupported_types(self):
        with self.assertRaisesRegex(NotImplementedError, "can't encode union types"):
            base.encode(123, Union[int, str])

        with self.assertRaisesRegex(NotImplementedError, "can't encode union types"):
            base.encode(123, Union[int, str, None])

        with self.assertRaisesRegex(NotImplementedError, "can't encode union types"):
            base.encode(123, Optional[Union[int, str]])

        with self.assertRaisesRegex(NotImplementedError, "can't encode object keys"):
            base.encode(123, Dict[Foo, str])

        with self.assertRaisesRegex(NotImplementedError, "failed to encode"):
            base.encode(123, Iterable[int])

        class Frob:
            pass

        with self.assertRaisesRegex(NotImplementedError, "failed to encode"):
            base.encode(123, Frob)

    def test_encode_bad_input(self):
        with self.assertRaisesRegex(NotImplementedError, r"failed to encode"):
            base.encode([1, 2], Foo)
