# Copyright 2021 John Reese
# Licensed under the MIT license

from unittest import TestCase

from jaymap.types import base, core

TEST_CAPABILITIES = {core.Capabilities.CORE: {"maxConcurrentRequests": 8}}
TEST_OBJECTS = (
    core.Account(
        name="foo@bar.com",
        is_personal=True,
        is_read_only=False,
        account_capabilities=TEST_CAPABILITIES,
    ),
    core.Session(
        capabilities=TEST_CAPABILITIES,
        accounts={
            core.Id("f123"): core.Account(
                name="foo@bar.com",
                is_personal=True,
                is_read_only=False,
                account_capabilities=TEST_CAPABILITIES,
            ),
        },
        primary_accounts={core.Capabilities.CORE: core.Id("f123")},
        username="foo@bar.com",
        api_url="https://localhost:4433/api/",
        download_url="https://localhost:4433/download/",
        upload_url="https://localhost:4433/upload/",
        event_source_url="https://localhost:4433/events/",
        state="aoeu1234",
    ),
    core.Request(
        using=[core.Capabilities.CORE],
        method_calls=[
            core.Invocation("func1", {"name": "foo"}, "c1"),
            core.Invocation("func2", {"name": "foo"}, "c2"),
        ],
    ),
    core.Response(
        method_responses=[
            core.Invocation("func1", {"name": "foo"}, "c1"),
            core.Invocation("func1", {"name": "foo"}, "c1"),
        ],
        session_state="aoeu2345",
    ),
)


class CoreTypes(TestCase):
    def test_id_class(self):
        for value in ("a", "1", "-", "u1234", "23a890Z_23-"):
            with self.subTest(f"valid id {value}"):
                id = core.Id(value)
                self.assertIsInstance(id, core.Id)
                self.assertEqual(id, value)

        for value in ("", "foo*bar", "foo()", "$100"):
            with self.subTest(f"invalid id {value}"):
                with self.assertRaisesRegex(ValueError, r"invalid Id"):
                    core.Id(value)

    def test_int_class(self):
        for value in (
            0,
            1,
            -1,
            1000,
            -10000,
            2 ** 53 - 1,
            -(2 ** 53) + 1,
            "0",
            "-1000",
        ):
            with self.subTest(f"valid int {value}"):
                id = core.Int(value)
                self.assertIsInstance(id, core.Int)
                self.assertEqual(id, int(value))

        for value in (2 ** 53, -(2 ** 53), 2 ** 54, -(2 ** 54)):
            with self.subTest(f"invalid int {value}"):
                with self.assertRaisesRegex(ValueError, r"Int -?\d+ [<>]"):
                    core.Int(value)

    def test_unsigned_int_class(self):
        for value in (0, 1, 1000, 1000000, 2 ** 53 - 1, "0", "1000"):
            with self.subTest(f"valid unsigned int {value}"):
                id = core.UnsignedInt(value)
                self.assertIsInstance(id, core.UnsignedInt)
                self.assertEqual(id, int(value))

        for value in (-1, -10, -10000000, -(2 ** 53), "-1", "-1000"):
            with self.subTest(f"invalid unsigned int {value}"):
                with self.assertRaisesRegex(ValueError, r"UnsignedInt -?\d+ [<>]"):
                    core.UnsignedInt(value)

    def test_is_datatype(self):
        for obj in TEST_OBJECTS:
            with self.subTest(obj.__class__.__name__):
                self.assertTrue(base.is_datatype(obj))
                self.assertTrue(base.is_datatype(obj.__class__))

    def test_datatype_encode_decode(self):
        for obj in TEST_OBJECTS:
            with self.subTest(obj.__class__.__name__):
                text = obj.to_json(indent=4)
                obj2 = obj.__class__.from_json(text)
                self.assertEqual(obj.__class__, obj2.__class__)
                self.assertEqual(obj, obj2)
