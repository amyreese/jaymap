# Copyright 2021 John Reese
# Licensed under the MIT license

from unittest import TestCase


class TypesTest(TestCase):
    def test_import(self):
        from jaymap.types import Invocation, Session

    def test_id_class(self):
        from jaymap.types import Id

        for value in ("a", "1", "-", "u1234", "23a890Z_23-"):
            with self.subTest(f"valid id {value}"):
                id = Id(value)
                self.assertIsInstance(id, Id)
                self.assertEqual(id, value)

        for value in ("", "foo*bar", "foo()", "$100"):
            with self.subTest(f"invalid id {value}"):
                with self.assertRaisesRegex(ValueError, "invalid Id"):
                    Id(value)

    def test_int_class(self):
        from jaymap.types import Int

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
                id = Int(value)
                self.assertIsInstance(id, Int)
                self.assertEqual(id, int(value))

        for value in (2 ** 53, -(2 ** 53), 2 ** 54, -(2 ** 54)):
            with self.subTest(f"invalid int {value}"):
                with self.assertRaisesRegex(ValueError, "Int -?\d+ [<>]"):
                    Int(value)

    def test_unsigned_int_class(self):
        from jaymap.types import UnsignedInt

        for value in (0, 1, 1000, 1000000, 2 ** 53 - 1, "0", "1000"):
            with self.subTest(f"valid unsigned int {value}"):
                id = UnsignedInt(value)
                self.assertIsInstance(id, UnsignedInt)
                self.assertEqual(id, int(value))

        for value in (-1, -10, -10000000, -(2 ** 53), "-1", "-1000"):
            with self.subTest(f"invalid unsigned int {value}"):
                with self.assertRaisesRegex(ValueError, "UnsignedInt -?\d+ [<>]"):
                    UnsignedInt(value)
