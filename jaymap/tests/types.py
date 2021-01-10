# Copyright 2021 John Reese
# Licensed under the MIT license

from unittest import TestCase

from jaymap import types


class TypesTest(TestCase):
    def test_id_class(self):
        for value in ("a", "1", "-", "u1234", "23a890Z_23-"):
            with self.subTest(f"valid id {value}"):
                id = types.Id(value)
                self.assertIsInstance(id, types.Id)
                self.assertEqual(id, value)

        for value in ("", "foo*bar", "foo()", "$100"):
            with self.subTest(f"invalid id {value}"):
                with self.assertRaisesRegex(ValueError, r"invalid Id"):
                    types.Id(value)

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
                id = types.Int(value)
                self.assertIsInstance(id, types.Int)
                self.assertEqual(id, int(value))

        for value in (2 ** 53, -(2 ** 53), 2 ** 54, -(2 ** 54)):
            with self.subTest(f"invalid int {value}"):
                with self.assertRaisesRegex(ValueError, r"Int -?\d+ [<>]"):
                    types.Int(value)

    def test_unsigned_int_class(self):
        for value in (0, 1, 1000, 1000000, 2 ** 53 - 1, "0", "1000"):
            with self.subTest(f"valid unsigned int {value}"):
                id = types.UnsignedInt(value)
                self.assertIsInstance(id, types.UnsignedInt)
                self.assertEqual(id, int(value))

        for value in (-1, -10, -10000000, -(2 ** 53), "-1", "-1000"):
            with self.subTest(f"invalid unsigned int {value}"):
                with self.assertRaisesRegex(ValueError, r"UnsignedInt -?\d+ [<>]"):
                    types.UnsignedInt(value)
